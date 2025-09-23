#!/usr/bin/env python3

import requests
import subprocess
from datetime import datetime, timedelta

def get_access_token():
    """Get access token from gcloud"""
    result = subprocess.run(['gcloud', 'auth', 'print-access-token'], 
                          capture_output=True, text=True)
    return result.stdout.strip()

def get_calendar_events():
    """Get calendar events using direct API call"""
    
    token = get_access_token()
    
    # Get events for the next 7 days
    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(days=7)).isoformat() + 'Z'
    
    print(f"🔍 Checking your calendar from {now.strftime('%Y-%m-%d %H:%M')} to {(now + timedelta(days=7)).strftime('%Y-%m-%d %H:%M')}")
    
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'timeMin': time_min,
        'timeMax': time_max,
        'maxResults': 10,
        'singleEvents': True,
        'orderBy': 'startTime'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('items', [])
            
            if not events:
                print('📅 No upcoming events found in your calendar.')
                return
            
            print(f"\n✅ Found {len(events)} upcoming events in your calendar:")
            print("=" * 60)
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                location = event.get('location', '')
                description = event.get('description', '')
                
                # Parse the datetime
                if 'T' in start:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = dt.strftime('%a %b %d, %Y at %I:%M %p')
                else:
                    time_str = start + ' (All day)'
                
                print(f"📅 {time_str}")
                print(f"   📝 {summary}")
                if location:
                    print(f"   📍 {location}")
                if description and len(description) < 100:
                    print(f"   💬 {description}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error accessing calendar: {e}")

if __name__ == '__main__':
    get_calendar_events()