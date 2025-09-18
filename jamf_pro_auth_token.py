import os
from dotenv import load_dotenv
# Import the jamf_session from the jamf_session module for persistent sessions
from jamf_session import jamf_session

# Load environment variables from .env file
load_dotenv()
jamf_pro_url = os.getenv("JAMF_PRO_URL")
jamf_pro_client_id = os.getenv("JAMF_PRO_CLIENT_ID")
jamf_pro_client_secret = os.getenv("JAMF_PRO_CLIENT_SECRET")


# Function to get Jamf Pro authentication token
def get_jamf_pro_auth_token():
    """
    Get a Jamf Pro authentication token using client credentials.
    """
    if not jamf_pro_url or not jamf_pro_client_id or not jamf_pro_client_secret:
        raise ValueError(
            "JAMF_PRO_URL, JAMF_PRO_CLIENT_ID, and JAMF_PRO_CLIENT_SECRET must be set in environment variables.")

    url = f"{jamf_pro_url}/api/v1/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "client_id": jamf_pro_client_id,
        "grant_type": "client_credentials",
        "client_secret": jamf_pro_client_secret
    }
    response = jamf_session.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception(f"Failed to get Jamf Pro auth token: {response.status_code} - {response.text}")
