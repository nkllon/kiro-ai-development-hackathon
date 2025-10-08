#!/usr/bin/env python3

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_credentials():
    """Get valid credentials for Google Calendar API"""
    creds = None
    
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Try to use application default credentials first
            try:
                from google.auth import default
                creds, project = default(scopes=SCOPES)
                print("✅ Using application default credentials")
            except Exception as e:
                print(f"❌ Could not use application default credentials: {e}")
                print("💡 You may need to run: gcloud auth application-default login")
                return None
        
        # Save the credentials for the next run
        if creds:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    
    return creds

def list_calendars():
    """List all Google calendars"""
    
    creds = get_credentials()
    if not creds:
        return
    
    try:
        # Build the Calendar API service
        service = build('calendar', 'v3', credentials=creds)
        
        print("🔍 Fetching your Google calendars...")
        
        # Call the Calendar API to list calendars
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        
        if not calendars:
            print('📅 No calendars found.')
            return
        
        print(f"\n✅ Found {len(calendars)} calendars:")
        print("=" * 80)
        
        for calendar in calendars:
            calendar_id = calendar.get('id', 'Unknown ID')
            summary = calendar.get('summary', 'No title')
            description = calendar.get('description', '')
            access_role = calendar.get('accessRole', 'Unknown')
            primary = calendar.get('primary', False)
            selected = calendar.get('selected', False)
            
            # Mark primary calendar
            primary_marker = " 🌟 (Primary)" if primary else ""
            selected_marker = " ✅ (Selected)" if selected else ""
            
            print(f"📅 {summary}{primary_marker}{selected_marker}")
            print(f"   📧 ID: {calendar_id}")
            print(f"   🔐 Access: {access_role}")
            if description:
                print(f"   📝 Description: {description}")
            print()
            
    except Exception as e:
        print(f"❌ Error accessing calendars: {e}")
        if "403" in str(e):
            print("💡 Make sure the Google Calendar API is enabled in your Google Cloud project")
            print("💡 Visit: https://console.cloud.google.com/apis/library/calendar-json.googleapis.com")

if __name__ == '__main__':
    list_calendars()