import os
import logging
import sys
import json
import urllib.request
import urllib.error
from urllib.parse import urljoin

# Get log level from environment variable, default to INFO
log_level = os.getenv('SHIPBOT_LOG_LEVEL', 'INFO').upper()
log_level_map = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR
}

log = logging.getLogger(__file__)
log.setLevel(log_level_map.get(log_level, logging.INFO))
handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(handler)

SHIPBOT_API_HOST = os.environ.get('SHIPBOT_API_HOST', 'https://api.shipbot.io')
FAILURE_MODE = os.environ.get('SHIPBOT_FAILURE_MODE', 'HARD').upper()

def handle_error(message, exception=None):
    """Handle errors based on failure mode"""
    log.error(message)
    if FAILURE_MODE == 'HARD':
        if exception:
            raise exception
        else:
            raise RuntimeError(message)

def load_artifact_config(config_path):
    """Load and validate artifact configuration file"""
    # Get the workspace directory
    workspace = os.getenv('GITHUB_WORKSPACE', '.')
    full_path = os.path.join(workspace, config_path)

    try:
        log.debug(f'Looking for config file at: {full_path}')
        with open(full_path, 'r') as f:
            config = json.load(f)

        if 'artifactId' not in config:
            raise ValueError(f'artifactId not found in artifact config: {config_path}')

        return config['artifactId']
    except FileNotFoundError:
        raise ValueError(f'Artifact config file not found: {config_path}')
    except json.JSONDecodeError:
        raise ValueError(f'Invalid JSON in artifact config: {config_path}')

def main(argv):
    # If no API key is provided, throw an error
    API_KEY = os.environ.get('SHIPBOT_API_KEY')
    if not API_KEY:
        raise ValueError('API_KEY is required')

    # Get deployment ID
    deployment_id = os.getenv('SHIPBOT_DEPLOYMENT_ID')

    if deployment_id is not None and deployment_id != '':
        log.info(f'Updating deployment {deployment_id}')

        # For deployment updates, validate status
        status = os.getenv('SHIPBOT_STATUS')
        if status not in ['SUCCEEDED', 'FAILED']:
            raise ValueError('SHIPBOT_STATUS must be either SUCCEEDED or FAILED when updating deployment')

        url = urljoin(SHIPBOT_API_HOST, f'/deployment/{deployment_id}')
        method = 'PATCH'

        payload = {'status': status}
    else:
        log.info(f'Creating new deployment')

        # Get artifactId from service config
        artifact_config = os.getenv('SHIPBOT_ARTIFACT_CONFIG')
        if not artifact_config:
            raise ValueError('SHIPBOT_ARTIFACT_CONFIG is required for new deployments')

        log.debug(f'Loading artifact config from: {artifact_config}')
        artifact_id = load_artifact_config(artifact_config)
        log.debug(f'Loaded artifactId: {artifact_id} from artifact config')

        # For new deployments, validate required fields
        version = os.getenv('SHIPBOT_VERSION')
        environment = os.getenv('SHIPBOT_ENVIRONMENT')
        commit_sha = os.getenv('SHIPBOT_COMMIT_SHA')
        user = os.getenv('SHIPBOT_USER')
        branch = os.getenv('SHIPBOT_BRANCH')

        if not version:
            raise ValueError('SHIPBOT_VERSION is required for new deployments')
        if not environment:
            raise ValueError('SHIPBOT_ENVIRONMENT is required for new deployments')
        if not commit_sha:
            raise ValueError('SHIPBOT_COMMIT_SHA is required for new deployments')
        if not user:
            raise ValueError('SHIPBOT_USER is required for new deployments')
        if not branch:
            raise ValueError('SHIPBOT_BRANCH is required for new deployments')

        log.info(f'Commit SHA: {commit_sha}')
        log.info(f'Branch: {branch}')

        url = urljoin(SHIPBOT_API_HOST, '/deployment')
        method = 'POST'

        # Initial payload with required fields
        payload = {
            'version': version,
            'environment': environment,
            'type': os.getenv('SHIPBOT_TYPE', 'STANDARD'),
            'artifactId': artifact_id,
            'commitSha': commit_sha,
            'user': user,
            'branch': branch
        }

        # Add optional fields if they exist
        optional_fields = {
            'status': 'SHIPBOT_STATUS',
            'changelog': 'SHIPBOT_CHANGE_LOG',
            'description': 'SHIPBOT_DESCRIPTION',
            'link': 'SHIPBOT_LINK'
        }

        for field, env_var in optional_fields.items():
            value = os.getenv(env_var)
            if value is not None and value != '':
                payload[field] = value

    # Headers
    headers = {
        'X-Api-Key': API_KEY,
        'Content-Type': 'application/json'
    }

    log.debug(f'Request URL: {url}')
    log.debug(f'Request Method: {method}')
    log.debug(f'Request Payload: {payload}')
    log.debug(f'Request Headers: {headers}')

    # Make the POST request
    try:
        # Create request
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method
        )

        # Make the request
        with urllib.request.urlopen(req) as response:
            response_text = response.read().decode('utf-8')
            log.debug(f'Response Text: {response_text}')

            status_code = response.status
            response_data = json.loads(response_text)
            log.info(f'Response: {response_data}')

            # Set output for GitHub Actions
            if 'id' in response_data:
                with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                    print(f"deploymentId={response_data['id']}", file=f)

            log.info(f'Status Code: {status_code}')

            if 200 <= status_code < 300:
                log.info('✅ Deployment successfully tracked in Shipbot')
            else:
                handle_error('❌ Deployment failed to track in Shipbot')

    except urllib.error.HTTPError as e:
        error_text = e.read().decode('utf-8')
        log.debug(f'Error Response Text: {error_text}')

        if e.code == 401:
            handle_error('❌ API Key was rejected by Shipbot')
            log.debug(f'API Key used: {API_KEY}')
        elif e.code == 422:
            log.error('❌ Invalid payload sent to Shipbot')
            log.info(f'Payload sent: {payload}')
            try:
                error_data = json.loads(error_text)
                log.info(f'Error response: {error_data}')
            except json.JSONDecodeError:
                log.info(f'Error response: {error_text}')
            handle_error('Invalid payload', e)
        elif e.code >= 500:
            log.error('❌ Shipbot server error occurred')
            log.debug(f'Payload sent: {payload}')
            try:
                error_data = json.loads(error_text)
                log.debug(f'Error response: {error_data}')
            except json.JSONDecodeError:
                log.debug(f'Error response: {error_text}')
            handle_error('Server error', e)
        else:
            handle_error(f'Error making request: {e}', e)
    except urllib.error.URLError as e:
        handle_error(f'Error making request: {e}', e)

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
