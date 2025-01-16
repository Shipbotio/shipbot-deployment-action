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

def main(argv):
    # If no API key is provided, throw an error
    API_KEY = os.environ.get('SHIPBOT_API_KEY')
    if not API_KEY:
        raise ValueError('API_KEY is required')

    # Headers
    headers = {
        'X-Api-Key': API_KEY,
        'Content-Type': 'application/json'
    }

    # Payload data with required fields
    payload = {
        'version': os.getenv('SHIPBOT_VERSION'),
        'environment': os.getenv('SHIPBOT_ENVIRONMENT'),
        'type': os.getenv('SHIPBOT_TYPE', 'STANDARD')
    }

    # Add optional fields if they exist
    optional_fields = {
        'artifactId': 'SHIPBOT_ARTIFACT_ID',
        'artifactName': 'SHIPBOT_ARTIFACT_NAME',
        'status': 'SHIPBOT_STATUS',
        'changelog': 'SHIPBOT_CHANGE_LOG',
        'commitSha': 'SHIPBOT_COMMITSHA',
        'description': 'SHIPBOT_DESCRIPTION',
        'link': 'SHIPBOT_LINK',
        'user': 'SHIPBOT_USER'
    }

    for field, env_var in optional_fields.items():
        value = os.getenv(env_var)
        if value is not None and value != '':
            payload[field] = value

    log.debug(f'Using API host: {SHIPBOT_API_HOST}')
    log.debug(f'Payload: {payload}')
    log.debug(f'Headers: {headers}')

    # Make the POST request
    try:
        # Create request
        url = urljoin(SHIPBOT_API_HOST, '/deployment')
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method='POST'
        )
        
        # Make the request
        with urllib.request.urlopen(req) as response:
            status_code = response.status
            try:
                response_data = json.loads(response.read().decode('utf-8'))
                log.info(f'Response: {response_data}')
            except json.JSONDecodeError:
                response_data = response.read().decode('utf-8')
                log.info(f'Response: {response_data}')

            log.info(f'Status Code: {status_code}')
            
            if 200 <= status_code < 300:
                log.info('✅ Deployment successfully tracked in Shipbot')
            else:
                handle_error('❌ Deployment failed to track in Shipbot')
        
    except urllib.error.HTTPError as e:
        if e.code == 401:
            handle_error('❌ API Key was rejected by Shipbot')
            log.debug(f'API Key used: {API_KEY}')
        elif e.code == 422:
            log.error('❌ Invalid payload sent to Shipbot')
            log.info(f'Payload sent: {payload}')
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                log.info(f'Error response: {error_data}')
            except json.JSONDecodeError:
                log.info(f'Error response: {e.read().decode("utf-8")}')
            handle_error('Invalid payload', e)
        elif e.code >= 500:
            log.error('❌ Shipbot server error occurred')
            log.debug(f'Payload sent: {payload}')
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                log.debug(f'Error response: {error_data}')
            except json.JSONDecodeError:
                log.debug(f'Error response: {e.read().decode("utf-8")}')
            handle_error('Server error', e)
        else:
            handle_error(f'Error making request: {e}', e)
    except urllib.error.URLError as e:
        handle_error(f'Error making request: {e}', e)

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
