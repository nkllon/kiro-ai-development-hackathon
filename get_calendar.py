#!/usr/bin/env python3

import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

def get_calendar_events():
    """Get calendar events using Application Default Credentials"""
    
    # Use the credentials we set up
    creds_path = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
    
    if not os.path.exists(creds_path):
        print("No credentials found. Run: gcloud auth application-default login")
        return
    
    # Load credentials
    with open(creds_path, 'r') as f:
        creds_data = json.load(f)
    
    creds = Credentials(
        token=creds_data.get('token'),
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data.get('token_uri'),
        client_id=creds_data.get('client_id'),
        client_secret=creds_data.get('client_secret'),
        scopes=['https://www.googleapis.com/auth/calendar.readonly']
    )
    
    # Refresh if needed
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    
    # Build the service
    service = build('calendar', 'v3', credentials=creds)
    
    # Get events for the next 7 days
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=7)).isoformat() + 'Z'
    
    print(f"Getting calendar events from {now.strftime('%Y-%m-%d %H:%M')} to {(now + timedelta(days=7)).strftime('%Y-%m-%d %H:%M')}")
    
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print('No upcoming events found.')
            return
        
        print(f"\nFound {len(events)} upcoming events:")
        print("=" * 50)
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            location = event.get('location', 'No location')
            
            # Parse the datetime
            if 'T' in start:
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_str = dt.strftime('%Y-%m-%d %H:%M')
            else:
                time_str = start + ' (All day)'
            
            print(f"📅 {time_str}")
            print(f"   {summary}")
            if location != 'No location':
                print(f"   📍 {location}")
            print()
            
    except Exception as e:
        print(f"Error accessing calendar: {e}")

if __name__ == '__main__':
    get_calendar_events()