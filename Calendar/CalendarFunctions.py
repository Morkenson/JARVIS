import os

from dotenv import load_dotenv
from msal import ConfidentialClientApplication
import requests

import Calendar.AccessToken

load_dotenv()

CLIENT_ID = os.getenv("MS_GRAPH_CLIENT_ID")
CLIENT_SECRET = os.getenv("MS_GRAPH_CLIENT_SECRET")
TENANT_ID = os.getenv("MS_GRAPH_TENANT_ID", "common")
AUTHORITY = os.getenv("MS_GRAPH_AUTHORITY", f"https://login.microsoftonline.com/{TENANT_ID}")
REDIRECT_URI = os.getenv("MS_GRAPH_REDIRECT_URI", "http://localhost")
SCOPES = os.getenv("MS_GRAPH_APP_SCOPES", "https://graph.microsoft.com/.default").split(",")
USER_ID = os.getenv("MS_GRAPH_USER_ID")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("MS_GRAPH_CLIENT_ID and MS_GRAPH_CLIENT_SECRET must be set.")
if not USER_ID:
    raise RuntimeError("MS_GRAPH_USER_ID must be set.")


def get_calendar_events():
    access_token = Calendar.AccessToken.generate_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://graph.microsoft.com/v1.0/me/events", headers=headers)
    if response.status_code == 200:
        events = response.json()
        return events["value"]
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def create_event():
    access_token = Calendar.AccessToken.generate_access_token()  # Ensure this fetches an application token
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    event_data = {
        "subject": "Meeting with Jarvis",
        "start": {"dateTime": "2024-12-05T10:00:00", "timeZone": "Central Standard Time"},
        "end": {"dateTime": "2024-12-05T11:00:00", "timeZone": "Central Standard Time"},
    }
    response = requests.post(f"https://graph.microsoft.com/v1.0/users/{user_id}/events", headers=headers, json=event_data)
    if response.status_code == 201:
        print("Event created successfully!")
    else:
        print(f"Failed to create event. Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        raise Exception(f"Error: {response.status_code}, {response.text}")

def delete_event(event_id, access_token):
    url = f"https://graph.microsoft.com/v1.0/me/events/{event_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:  # 204 indicates successful deletion
        print("Event deleted successfully!")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def update_event(event_id, access_token, updated_data):
    url = f"https://graph.microsoft.com/v1.0/me/events/{event_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.patch(url, headers=headers, json=updated_data)

    if response.status_code == 200:  # 200 indicates successful update
        print("Event updated successfully!")
    else:
        print(f"Error: {response.status_code}, {response.text}")

