import httpx
from datetime import datetime, timezone, timedelta
from app.helpers import db_helper as dbh
from sqlalchemy.orm import Session
from fastapi import HTTPException, Query
from pydantic import BaseModel
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
import os

GOOGLE_MEET_REDIRECT_URL = os.getenv('GOOGLE_MEET_REDIRECT_URL')
GOOGLE_MEET_CLIENT_ID = os.getenv('GOOGLE_MEET_CLIENT_ID')
GOOGLE_MEET_CLIENT_SECRET = os.getenv('GOOGLE_MEET_CLIENT_SECRET')

class CreateGoogleMeetingRequest(BaseModel):
    token: str
    summary: str
    start_time: str  # Expected format: 'YYYY-MM-DDTHH:MM:SS'
    duration_minutes: int
    time_zone: str  # Time zone (e.g., "Asia/Kolkata", "America/New_York")
    attendees: list[str]

def get_tokens_from_auth_code(code: str):
    url = "https://oauth2.googleapis.com/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "code": code,
        "client_id": GOOGLE_MEET_CLIENT_ID,
        "client_secret": GOOGLE_MEET_CLIENT_SECRET,
        "redirect_uri": GOOGLE_MEET_REDIRECT_URL,
        "grant_type": "authorization_code"
    }

    response = httpx.post(url, data=data, headers=headers)
    print('response',response)
    return response.json()

def refresh_google_access_token(google_refresh_token: str=None):
     token_url = "https://oauth2.googleapis.com/token"
     headers = {"Content-Type": "application/x-www-form-urlencoded"}

     data = {
         "client_id": GOOGLE_MEET_CLIENT_ID,
         "client_secret": GOOGLE_MEET_CLIENT_SECRET,
         "refresh_token": google_refresh_token,
         "grant_type": "refresh_token"
     }

     response = httpx.post(token_url, data=data, headers=headers)
     return response.json()

def validate_access_token(credentials,integration,email,session: Session):
    if credentials.get('expires_in') < datetime.now(timezone.utc).isoformat():
        response = refresh_google_access_token(credentials['refresh_token'])
        expires_in = datetime.now(timezone.utc) + timedelta(seconds=response.get('expires_in'))
        expires_in = expires_in.isoformat()
        credentials = {
            "refresh_token": response.get('refresh_token'),
            "access_token": response.get('access_token'),
            "expires_in": expires_in
        }
        integration.credentials.update(credentials)
        integration.meta.update(dbh.update_meta(meta=integration.meta, email=email))
        integration.update(session=session)
    else:
        response = credentials
    return response

def get_google_service(token: str):
    creds = Credentials(token)
    return build('calendar', 'v3', credentials=creds)

async def create_meeting(request: CreateGoogleMeetingRequest):
    token = request.token
    summary = request.summary
    start_time_str = request.start_time
    duration_minutes = request.duration_minutes
    time_zone = request.time_zone
    attendees = request.attendees

    if not token:
        raise HTTPException(status_code=400, detail="OAuth token is required")

    # Convert start_time string to datetime object in the given time zone
    try:
        user_tz = pytz.timezone(time_zone)
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
        start_time = user_tz.localize(start_time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid start_time or time_zone: {str(e)}")

    # Calculate end time
    end_time = start_time + timedelta(minutes=duration_minutes)

    # Convert back to ISO format
    start_time_iso = start_time.strftime("%Y-%m-%dT%H:%M:%S")
    end_time_iso = end_time.strftime("%Y-%m-%dT%H:%M:%S")

    service = get_google_service(token)

    event = {
        'summary': summary,
        'start': {'dateTime': start_time_iso, 'timeZone': time_zone},
        'end': {'dateTime': end_time_iso, 'timeZone': time_zone},
        'attendees': [{'email': email} for email in attendees],
        'conferenceData': {
            'createRequest': {
                'requestId': 'sample123',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        }
    }

    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1,
        sendUpdates='all'
    ).execute()

    return {
        "message": "Meeting created successfully!",
        "meeting_link": event['htmlLink'],
        "start_time": start_time_iso,
        "end_time": end_time_iso,
        "time_zone": time_zone,
        "attendees": attendees
    }