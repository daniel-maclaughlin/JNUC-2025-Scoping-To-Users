import os
from dotenv import load_dotenv
import requests
import msal

# Load environment variables from .env file
load_dotenv()
tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
secret_value = os.getenv("SECRET_VALUE")


# Function to get Microsoft Graph API access token
def get_access_token():
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    scope = ["https://graph.microsoft.com/.default"]

    # Acquire token
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=secret_value
    )
    result = app.acquire_token_for_client(scopes=scope)

    if "access_token" in result:
        access_token = result["access_token"]
        return access_token
    else:
        print(f"Error acquiring token: {result.get('error')}, {result.get('error_description')}")
        return None


# Get all user group membership from Microsoft Graph API
def get_all_user_groups(access_token, user_id):
    graph_url = "https://graph.microsoft.com/v1.0"
    transitive_url = f"{graph_url}/users/{user_id}/transitiveMemberOf"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(transitive_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching groups: {response.status_code} - {response.text}")
        return None


# Get user details by email from Microsoft Graph API
def get_user_details(access_token, user_email):
    graph_url = "https://graph.microsoft.com/v1.0"
    url = f"{graph_url}/users?$filter=userPrincipalName eq '{user_email}'"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching user details: {response.status_code} - {response.text}")
        return None
