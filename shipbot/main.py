import os
import logging
import sys
import requests

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
        response = requests.post(f'{SHIPBOT_API_HOST}/deployment', headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        
        log.info(f'Status Code: {response.status_code}')
        try:
            log.info(f'Response: {response.json()}')
        except requests.exceptions.JSONDecodeError:
            log.info(f'Response: {response.text}')
        
        if response.ok:
            log.info('✅ Deployment successfully tracked in Shipbot')
        else:
            log.error('❌ Deployment failed to track in Shipbot')
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            handle_error('❌ API Key was rejected by Shipbot', e)
            log.debug(f'API Key used: {API_KEY}')
        elif response.status_code == 422:
            log.error('❌ Invalid payload sent to Shipbot')
            log.info(f'Payload sent: {payload}')
            try:
                log.info(f'Error response: {response.json()}')
            except requests.exceptions.JSONDecodeError:
                log.info(f'Error response: {response.text}')
            handle_error('Invalid payload', e)
        elif response.status_code >= 500:
            log.error('❌ Shipbot server error occurred')
            log.debug(f'Payload sent: {payload}')
            try:
                log.debug(f'Error response: {response.json()}')
            except requests.exceptions.JSONDecodeError:
                log.debug(f'Error response: {response.text}')
            handle_error('Server error', e)
        else:
            handle_error(f'Error making request: {e}', e)

    except requests.exceptions.RequestException as e:
        handle_error(f'Error making request: {e}', e)

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv)
