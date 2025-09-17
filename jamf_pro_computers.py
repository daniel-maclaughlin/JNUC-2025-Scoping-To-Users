import os
from dotenv import load_dotenv
from jamf_session import jamf_session


json_header_type = 'application/json'
load_dotenv()
jamf_pro_url = os.getenv("JAMF_PRO_URL")


def get_jamf_pro_computers(jamf_pro_token, username):
    """
    Retrieve all computers from Jamf Pro that match the given email.
    """
    url = f'{jamf_pro_url}/api/v1/computers-inventory?section=GENERAL&section=HARDWARE&section=GROUP_MEMBERSHIPS&filter=userAndLocation.email=={username}'
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
        for computer in data.get('results', []):
            for group in computer.get('groupMemberships', []):
                if not group.get('smartGroup'):
                    static_group_record = {
                        'id': group.get('groupId'),
                        'groupName': group.get('groupName')
                    }
                    static_groups.append(static_group_record)

            computer_data = {
                'id': computer.get('id'),
                'name': computer.get('general', {}).get('name'),
                'serial_number': computer.get('hardware', {}).get('serialNumber'),
                'group_memberships': static_groups
            }
            response_data.append(computer_data)
        return response_data
    except jamf_session.exceptions.RequestException as error:
        print(f'Error getting computers for user {username}: {error}')
        return []