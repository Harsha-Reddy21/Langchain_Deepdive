#!/usr/bin/env python3
"""
Test script to verify Gmail authentication
"""
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

def test_gmail_auth():
    """Test Gmail authentication"""
    print("Testing Gmail authentication...")
    
    creds = None
    
    # Try to load existing credentials
    if os.path.exists('token.json'):
        print("Found existing token.json, trying to use it...")
        try:
            with open('token.json', 'r') as token:
                token_data = json.load(token)
            
            creds = Credentials(
                token=None,
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes', SCOPES)
            )
            
            # Try to refresh the token
            if creds.expired and creds.refresh_token:
                print("Token expired, refreshing...")
                creds.refresh(Request())
                print("Token refreshed successfully!")
            
        except Exception as e:
            print(f"Error with existing token: {e}")
            creds = None
    
    # If no valid credentials, start OAuth flow
    if not creds or not creds.valid:
        print("Starting OAuth flow...")
        
        # Use credential.json for OAuth client configuration
        if not os.path.exists('credential.json'):
            print("credential.json not found. Please provide your OAuth client credentials as credential.json.")
            return False
        try:
            flow = InstalledAppFlow.from_client_secrets_file('credential.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("OAuth flow completed successfully!")
            
            # Save new credentials
            token_data = {
                'refresh_token': creds.refresh_token,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'token_uri': creds.token_uri,
                'scopes': creds.scopes
            }
            
            with open('token.json', 'w') as token:
                json.dump(token_data, token, indent=2)
            print("New credentials saved to token.json")
            
        except Exception as e:
            print(f"OAuth flow failed: {e}")
            return False
    
    # Test Gmail API
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Try to get user profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"Successfully authenticated as: {profile['emailAddress']}")
        
        # Try to list a few messages
        messages = service.users().messages().list(userId='me', maxResults=1).execute()
        print(f"Successfully accessed Gmail API. Found {len(messages.get('messages', []))} messages.")
        
        return True
        
    except Exception as e:
        print(f"Gmail API test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_gmail_auth()
    if success:
        print("\n✅ Authentication test PASSED!")
    else:
        print("\n❌ Authentication test FAILED!") 