from microsoft_group_membership import get_access_token, get_user_details, get_all_user_groups
from jamf_pro_auth_token import get_jamf_pro_auth_token
from jamf_pro_computers import get_jamf_pro_computers
from jamf_pro_devices import get_jamf_pro_devices
from jamf_pro_computer_groups import add_computer_to_group, remove_computer_from_group
from jamf_pro_mobile_groups import add_device_to_group, remove_device_from_group

# This section would typically be another function to receive email input
# Insert your email here to check group memberships
email = 'sara.newman@jamfse.io'

# Acquire tokens
intune_token = get_access_token()
jamf_pro_auth_token = get_jamf_pro_auth_token()


# Function to compare two lists and determine additions/removals
def sync_lists(source_list, target_list):
    to_add = list(set(source_list) - set(target_list))
    to_remove = list(set(target_list) - set(source_list))
    return to_add, to_remove


# Main logic
# Ensure tokens are acquired
if not intune_token or not jamf_pro_auth_token:
    print('Failed to acquire access token.')
    exit(1)

# Get user details from Entra ID
user_data = get_user_details(intune_token, email)
entra_team_groups = []
if user_data:
    user_id = user_data['value'][0]['id']
    print('############ Direct Groups Membership: ############')
    direct_groups = get_all_user_groups(intune_token, user_id)
    if direct_groups:
        for group in direct_groups['value']:
            group_name = group.get('displayName', 'No Display Name')
            if group_name.startswith('Team'):
                entra_team_groups.append(group_name)
    else:
        user_data['groups'] = []

# For each Entra User group, check Jamf Pro group memberships for computers and devices
for entra_group in entra_team_groups:
    print(f"User: {email} Member of Group: {entra_group} according to Entra")
    print('############ Checking Jamf Pro for Computers Group Membership: ############')
    jamf_pro_computers = get_jamf_pro_computers(jamf_pro_auth_token, email)
    for computer in jamf_pro_computers:
        computer_id = computer.get('id')
        # Extract Jamf Pro group names and map to IDs
        jamf_groups = computer.get('group_memberships', [])
        jamf_group_name_to_id = {g['groupName']: g['id'] for g in jamf_groups}

        computer_group_to_add, computer_group_to_remove = sync_lists([entra_group], list(jamf_group_name_to_id.keys()))
        # Track IDs for add/remove
        to_add = [{'id': None, 'groupName': name} for name in computer_group_to_add]  # No ID yet for groups to add
        to_remove = [{'id': jamf_group_name_to_id[name], 'groupName': name} for name in computer_group_to_remove]

        if to_add:
            group_id = to_add[0]['id']
            group_name = to_add[0]['groupName']
            print(f'Adding computer {computer_id} to group {group_name}')
            add_computer = add_computer_to_group(jamf_pro_auth_token, entra_group, computer_id, group_id)

        if to_remove:
            group_id = to_remove[0]['id']
            group_name = to_remove[0]['groupName']
            print(f'Removing computer {computer_id} from group {group_name}')
            remove_computer = remove_computer_from_group(jamf_pro_auth_token, entra_group, computer_id, group_id)

    print('############ Checking Jamf Pro for Mobile Group Membership: ############')
    jamf_pro_devices = get_jamf_pro_devices(jamf_pro_auth_token, email)
    for device in jamf_pro_devices:
        device_id = device.get('id')
        # Extract Jamf Pro group names and map to IDs
        jamf_groups = device.get('group_memberships', [])
        jamf_group_name_to_id = {g['groupName']: g['id'] for g in jamf_groups}

        device_group_to_add, device_group_to_remove = sync_lists([entra_group], list(jamf_group_name_to_id.keys()))
        # Track IDs for add/remove
        to_add = [{'id': None, 'groupName': name} for name in device_group_to_add]  # No ID yet for groups to add
        to_remove = [{'id': jamf_group_name_to_id[name], 'groupName': name} for name in device_group_to_remove]

        if to_add:
            group_id = to_add[0]['id']
            group_name = to_add[0]['groupName']
            print(f'Adding device {device_id} to group {group_name}')
            add_device = add_device_to_group(jamf_pro_auth_token, entra_group, device_id, group_id)
        if to_remove:
            group_id = to_remove[0]['id']
            group_name = to_remove[0]['groupName']
            print(f'removing device {device_id} from group {group_name}')
            remove_device = remove_device_from_group(jamf_pro_auth_token, entra_group, device_id, group_id)
