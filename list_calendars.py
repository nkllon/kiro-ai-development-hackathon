#!/usr/bin/env python3

import requests
import subprocess
import json

def get_access_token():
    """Get access token from gcloud"""
    try:
        result = subprocess.run(['gcloud', 'auth', 'print-access-token'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting access token: {e}")
        print("💡 Try running: gcloud auth login")
        return None

def list_calendars():
    """List all Google calendars using direct API call"""
    
    token = get_access_token()
    if not token:
        return
    
    print("🔍 Fetching your Google calendars...")
    
    url = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            calendars = data.get('items', [])
            
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
                
                # Mark primary calendar
                primary_marker = " 🌟 (Primary)" if primary else ""
                
                print(f"📅 {summary}{primary_marker}")
                print(f"   📧 {calendar_id}")
                print(f"   🔐 Access: {access_role}")
                if description:
                    print(f"   📝 {description}")
                print()
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 401:
                print("💡 Try running: gcloud auth login")
            elif response.status_code == 403:
                print("💡 You may need to enable the Calendar API or check permissions")
            
    except Exception as e:
        print(f"❌ Error accessing calendars: {e}")

if __name__ == '__main__':
    list_calendars()