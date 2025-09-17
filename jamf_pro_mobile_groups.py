import os
from dotenv import load_dotenv
import urllib.parse
import xml.etree.ElementTree as ET
from time import sleep
from jamf_session import jamf_session

xml_header_type = 'application/xml'
json_header_type = 'application/json'
load_dotenv()
jamf_pro_url = os.getenv("JAMF_PRO_URL")


# Function to create the XMl for the Static group if missing
def build_device_group_xml(group_name):
    mobile_device_group = ET.Element('mobile_device_group')
    ET.SubElement(mobile_device_group, 'name').text = group_name
    ET.SubElement(mobile_device_group, 'is_smart').text = 'false'
    return ET.tostring(mobile_device_group, encoding='utf-8', method='xml').decode('utf-8')


def build_device_addition_xml(device_id):
    mobile_device_group = ET.Element('mobile_device_group')
    mobile_device_additions = ET.SubElement(mobile_device_group, 'mobile_device_additions')
    mobile_device = ET.SubElement(mobile_device_additions, 'mobile_device')
    ET.SubElement(mobile_device, 'id').text = str(device_id)
    # You can add more fields if needed
    return ET.tostring(mobile_device_group, encoding='utf-8', method='xml').decode('utf-8')


def build_computer_removal_xml(device_id):
    mobile_device_group = ET.Element('mobile_device_group')
    mobile_device_deletions = ET.SubElement(mobile_device_group, 'mobile_device_deletions')
    mobile_device = ET.SubElement(mobile_device_deletions, 'mobile_device')
    ET.SubElement(mobile_device, 'id').text = str(device_id)
    # You can add more fields if needed
    return ET.tostring(mobile_device_group, encoding='utf-8', method='xml').decode('utf-8')


def create_static_computer_group(jamf_pro_token, group_name):
    """
    Create a static computer group in Jamf Pro.
    """
    url = f'{jamf_pro_url}/JSSResource/mobiledevicegroups/id/0'

    headers = {
        'Accept': xml_header_type,
        'Content-Type': xml_header_type,
        'Authorization': f'Bearer {jamf_pro_token}'
    }

    xml_data = build_device_group_xml(group_name)
    try:
        response = jamf_session.post(url, data=xml_data, headers=headers)
        if response.status_code == 201:
            print(f'Successfully created static device group: {group_name}')
            return True
        else:
            return None
    except jamf_session.exceptions.RequestException as error:
        print(f'Error creating static device group: {error}')
        return None


def get_group_id(jamf_pro_token, group_name):
    """
    Retrieve the ID of a static computer group by its name.
    """
    url = f'{jamf_pro_url}/JSSResource/mobiledevicegroups/name/{group_name}'
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
            sleep(1)
            return get_group_id(jamf_pro_token, group_name)
        response.raise_for_status()
        data = response.json()
        return data.get('mobile_device_group', {}).get('id')
    except jamf_session.exceptions.RequestException as error:
        print(f'Error getting group ID for {group_name}: {error}')
        return None


def add_device_to_group(jamf_pro_token, group_name, device_id, group_id=None):
    """
    Add a device to a static group in Jamf Pro.
    """
    if group_id is None:
        group_id = get_group_id(jamf_pro_token, group_name)
    print(f'Adding device {device_id} to group {group_id}')
    url = f'{jamf_pro_url}/JSSResource/mobiledevicegroups/id/{group_id}'
    headers = {
        'Accept': xml_header_type,
        'Content-Type': xml_header_type,
        'Authorization': f'Bearer {jamf_pro_token}'
    }
    data = build_device_addition_xml(device_id)
    try:
        response = jamf_session.put(url, data=data, headers=headers)
        return response.status_code
    except jamf_session.exceptions.RequestException as error:
        print(f'Error adding device to group: {error}')
        return None


def remove_device_from_group(jamf_pro_token, group_name, device_id, group_id=None):
    """
    Remove a device from a static group in Jamf Pro.
    """
    if group_id is None:
        group_id = get_group_id(jamf_pro_token, group_name)

    url = f'{jamf_pro_url}/JSSResource/mobiledevicegroups/id/{group_id}'
    headers = {
        'Accept': xml_header_type,
        'Content-Type': xml_header_type,
        'Authorization': f'Bearer {jamf_pro_token}'
    }
    data = build_computer_removal_xml(device_id)
    try:
        response = jamf_session.put(url, data=data, headers=headers)
        return response.status_code
    except jamf_session.exceptions.RequestException as error:
        print(f'Error removing device from group: {error}')
        return None
