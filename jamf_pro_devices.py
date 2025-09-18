import os
from dotenv import load_dotenv
from jamf_session import jamf_session


json_header_type = 'application/json'
# Load environment variables from .env file
load_dotenv()
jamf_pro_url = os.getenv("JAMF_PRO_URL")

# Function to get all mobile devices for a specific user by email
def get_jamf_pro_devices(jamf_pro_token, username):
    """
    Retrieve all Mobile Devices from Jamf Pro that match the given email.
    """
    url = f'{jamf_pro_url}/api/v2/mobile-devices/detail?section=GENERAL&section=HARDWARE&section=GROUPS&filter=emailAddress=={username}'
    headers = {
        'Accept': json_header_type,
        'Content-Type': json_header_type,
        'Authorization': f'Bearer {jamf_pro_token}'
    }

    try:
        response = jamf_session.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        response_data = []
        static_groups = []
        for device in data.get('results', []):
            for group in device.get('groups', []):
                if not group.get('smart'):
                    static_group_record = {
                        'id': group.get('groupId'),
                        'groupName': group.get('groupName')
                    }
                    static_groups.append(static_group_record)
            device_data = {
                'id': device.get('mobileDeviceId'),
                'name': device.get('general', {}).get('displayName'),
                'serial_number': device.get('hardware', {}).get('serialNumber'),
                'group_memberships': static_groups
            }
            response_data.append(device_data)
        return response_data
    except jamf_session.exceptions.RequestException as error:
        print(f'Error getting computers for user {username}: {error}')
        return []