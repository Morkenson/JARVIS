import requests
import webbrowser
from datetime import datetime
import json
import os

import msal
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
APP_ID = os.getenv('MS_GRAPH_CLIENT_ID')
TENANT_ID = os.getenv("MS_GRAPH_TENANT_ID", "common")
SCOPES = [scope.strip() for scope in os.getenv("MS_GRAPH_SCOPES", "Calendars.ReadWrite").split(",") if scope.strip()]

if not APP_ID:
    raise RuntimeError("MS_GRAPH_CLIENT_ID is not set.")
if not SCOPES:
    raise RuntimeError("MS_GRAPH_SCOPES must contain at least one scope.")

def generate_access_token():
    # Save Session Token as a token file
    access_token_cache = msal.SerializableTokenCache()

    # read the token file
    if os.path.exists('ms_graph_api_token.json'):
            with open("ms_graph_api_token.json", "r") as token_file:
                try:
                    token_detail = json.load(token_file)
                    print("Token detail:", token_detail)  # Debugging
                    if 'AccessToken' in token_detail:
                        token_key = list(token_detail['AccessToken'].keys())[0]
                        token_expiration = datetime.fromtimestamp(
                            int(token_detail['AccessToken'][token_key]['expires_on'])
                        )
                        if datetime.now() > token_expiration:
                            print("Token expired. Removing cache file.")
                            os.remove('ms_graph_api_token.json')
                            access_token_cache = msal.SerializableTokenCache()
                    else:
                        print("No valid AccessToken found. Re-authenticating...")
                        os.remove('ms_graph_api_token.json')
                        access_token_cache = msal.SerializableTokenCache()
                except json.JSONDecodeError:
                    print("Invalid or empty token cache file. Re-authenticating...")
                    os.remove('ms_graph_api_token.json')
                    access_token_cache = msal.SerializableTokenCache()

    # assign a SerializableTokenCache object to the client instance
    client = msal.PublicClientApplication(
        client_id=APP_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=access_token_cache
    )

    accounts = client.get_accounts()
    if accounts:
        # load the session
        token_response = client.acquire_token_silent(SCOPES, accounts[0])
    else:
        # authetnicate your accoutn as usual
        flow = client.initiate_device_flow(scopes=SCOPES)
        print("Flow response:", flow)
        #print('user_code: ' + flow['user_code'])
        webbrowser.open('https://microsoft.com/devicelogin')
        token_response = client.acquire_token_by_device_flow(flow)

    with open('ms_graph_api_token.json', 'w') as _f:
        _f.write(access_token_cache.serialize())
    
    return token_response