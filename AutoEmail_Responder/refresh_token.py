#!/usr/bin/env python3
import json
import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_refresh_token():
    """Get refresh token for Google OAuth authentication."""
    try:
        # Path to credentials.json file
        credentials_path = Path.cwd() / 'credentials.json'
        
        if not credentials_path.exists():
            print("Error: credentials.json file not found in current directory")
            return
        
        # Load client secrets from credentials.json
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path), 
            SCOPES
        )
        
        # Run the OAuth flow
        credentials = flow.run_local_server(port=0)
        
        # Get the refresh token
        refresh_token = credentials.refresh_token
        client_id = credentials.client_id
        client_secret = credentials.client_secret
        
        print(f'\nRefresh Token: {refresh_token}')
        print(f'\nClient ID: {client_id}')
        print(f'\nClient Secret: {client_secret}')
        
        # Save credentials to a file
        token_data = {
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
            'token_uri': credentials.token_uri,
            'scopes': credentials.scopes
        }
        
        with open('token.json', 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print('\nCredentials saved to token.json')
        
    except Exception as error:
        print(f'Error getting refresh token: {error}')

if __name__ == '__main__':
    get_refresh_token() 