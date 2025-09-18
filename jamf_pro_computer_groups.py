import os
from dotenv import load_dotenv
import urllib.parse
import xml.etree.ElementTree as ET
from jamf_session import jamf_session

xml_header_type = 'application/xml'
json_header_type = 'application/json'
# Load environment variables from .env file
load_dotenv()
jamf_pro_url = os.getenv("JAMF_PRO_URL")


# Function to create the XMl for the Static group if missing
def build_computer_group_xml(group_name):
    computer_group = ET.Element('computer_group')
    ET.SubElement(computer_group, 'name').text = group_name
    ET.SubElement(computer_group, 'is_smart').text = 'false'
    return ET.tostring(computer_group, encoding='utf-8', method='xml').decode('utf-8')


# Function to create the XML for adding computers from the static group
def build_computer_addition_xml(computer_id):
    computer_group = ET.Element('computer_group')
    computer_addition = ET.SubElement(computer_group, 'computer_additions')
    computer = ET.SubElement(computer_addition, 'computer')
    ET.SubElement(computer, 'id').text = str(computer_id)
    # You can add more fields if needed
    return ET.tostring(computer_group, encoding='utf-8', method='xml').decode('utf-8')


# Function to create the XML for removing computers from the static group
def build_computer_removal_xml(computer_id):
    computer_group = ET.Element('computer_group')
    computer_addition = ET.SubElement(computer_group, 'computer_deletions')
    computer = ET.SubElement(computer_addition, 'computer')
    ET.SubElement(computer, 'id').text = str(computer_id)
    # You can add more fields if needed
    return ET.tostring(computer_group, encoding='utf-8', method='xml').decode('utf-8')


# Function to create a static computer group in Jamf Pro
def create_static_computer_group(jamf_pro_token, group_name):
    """
    Create a static computer group in Jamf Pro.
    """
    url = f'{jamf_pro_url}/JSSResource/computergroups/id/0'

    headers = {
        'Accept': xml_header_type,
        'Content-Type': xml_header_type,
        'Authorization': f'Bearer {jamf_pro_token}'
    }

    xml_data = build_computer_group_xml(group_name)
    try:
        response = jamf_session.post(url, data=xml_data, headers=headers)
        if response.status_code == 201:
            print(f'Successfully created static computer group: {group_name}')
            return True
        else:
            return None
    except jamf_session.exceptions.RequestException as error:
        print(f'Error creating static computer group: {error}')
        return None


# Function to get the ID of a static computer group by name
def get_group_id(jamf_pro_token, group_name):
    """
    Retrieve the ID of a static computer group by its name.
    """
    url = f'{jamf_pro_url}/JSSResource/computergroups/name/{group_name}'
    encoded_url = urllib.parse.quote(url, safe=':/')

    headers = {
        'Accept': json_header_type,
        'Content-Type': json_header_type,
        'Authorization': f'Bearer {jamf_pro_token}'
    }

    try:
        response = jamf_session.get(encoded_url, headers=headers)
        if response.status_code == 404:
            print(f'Group {group_name} not found. Creating it now.')
            create_static_computer_group(jamf_pro_token, group_name)
            return get_group_id(jamf_pro_token, group_name)
        response.raise_for_status()
        data = response.json()
        return data.get('computer_group', {}).get('id')
    except jamf_session.exceptions.RequestException as error:
        print(f'Error getting group ID for {group_name}: {error}')
        return None


# Function to add a computer to a static group
def add_computer_to_group(jamf_pro_token, group_name, computer_id, group_id=None):
    """
    Add a computer to a static group in Jamf Pro.
    """
    if group_id is None:
        group_id = get_group_id(jamf_pro_token, group_name)

    url = f'{jamf_pro_url}/JSSResource/computergroups/id/{group_id}'
    headers = {
        'Accept': xml_header_type,
        'Content-Type': xml_header_type,
        'Authorization': f'Bearer {jamf_pro_token}'
    }
    data = build_computer_addition_xml(computer_id)
    try:
        response = jamf_session.put(url, data=data, headers=headers)
        return response.status_code
    except jamf_session.exceptions.RequestException as error:
        print(f'Error adding computer to group: {error}')
        return None


# Function to remove a computer from a static group
def remove_computer_from_group(jamf_pro_token, group_name, computer_id, group_id=None):
    """
    Remove a computer from a static group in Jamf Pro.
    """
    if group_id is None:
        group_id = get_group_id(jamf_pro_token, group_name)

    url = f'{jamf_pro_url}/JSSResource/computergroups/id/{group_id}'
    headers = {
        'Accept': xml_header_type,
        'Content-Type': xml_header_type,
        'Authorization': f'Bearer {jamf_pro_token}'
    }
    data = build_computer_removal_xml(computer_id)
    try:
        response = jamf_session.put(url, data=data, headers=headers)
        return response.status_code
    except jamf_session.exceptions.RequestException as error:
        print(f'Error removing computer from group: {error}')
        return None
