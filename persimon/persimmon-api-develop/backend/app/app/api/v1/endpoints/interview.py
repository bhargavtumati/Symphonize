from fastapi import HTTPException, APIRouter
import requests
import json
from datetime import datetime
from pytz import timezone
from app.api.v1.endpoints.models.interview_model import InterviewDetails

router = APIRouter()

# Define your Azure AD credentials
tenant_id = "enter your tenant id"
client_id = "enter your client id"
client_secret = "enter your client secret"

"""
These credentials are necessary because they enable your app to interact with Microsoft Teams through the Microsoft Graph API. Here's a breakdown of why each credential is required:
tenant_id: This identifies your Azure Active Directory (AAD) tenant. It's crucial for the OAuth2 authentication process, allowing Microsoft to know which tenant is requesting access.
client_id: This is the unique identifier for your app registration within Azure AD. It helps Microsoft identify your app during authentication and authorization processes.
client_secret: This is a secret key used in combination with the client_id to securely authenticate your app when it requests an access token from Azure AD. Think of it as a password for your app.
"""

@router.post("/schedule-interview")
async def schedule_interview(details: InterviewDetails):
    try:
        # Get Access Token...
        access_token = get_access_token()
        print(access_token)
        # Create Microsoft Teams meeting link...
        meeting_link = create_teams_meeting(details, access_token)
        print(meeting_link)
        # Send notifications...
        send_notification_emails(details, meeting_link)
        
        return {"message": "Interview scheduled successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule interview: {str(e)}")

def get_access_token():
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'client_id': client_id,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    
    return response.json().get("access_token")

def create_teams_meeting(details, access_token):
    url = f"https://graph.microsoft.com/v1.0/{details.interviewer_email}/onlineMeetings"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    start_datetime = datetime.fromisoformat(f"{details.date}T{details.start_time}").astimezone(timezone(details.timezone)).isoformat()
    end_datetime = datetime.fromisoformat(f"{details.date}T{details.end_time}").astimezone(timezone(details.timezone)).isoformat()
    
    payload = {
        "subject": details.interview_title,
        "startDateTime": start_datetime,
        "endDateTime": end_datetime,
        "participants": {
            "attendees": [
                {"upn": details.applicant_email, "role": "attendee"}
            ]
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json().get("joinWebUrl")

def send_notification_emails(details, meeting_link):
    # Integrate with an email service (like SendGrid, SMTP, etc.) to send emails
    # Example below uses a placeholder function to demonstrate
    
    email_content = f"""
    <p>Hello,</p>
    <p>The following interview has been scheduled:</p>
    <ul>
        <li><strong>Date:</strong> {details.date}</li>
        <li><strong>Time:</strong> {details.start_time} - {details.end_time} ({details.timezone})</li>
        <li><strong>Platform:</strong> Microsoft Teams</li>
        <li><strong>Meeting Link:</strong> <a href="{meeting_link}">Join Meeting</a></li>
    </ul>
    <p>{details.description}</p>
    <p><strong>Additional Details:</strong></p>
    <p>{json.dumps(details.additional_details)}</p>
    <p>Best regards,<br>Your HR Team</p>
    """
    # Implement email sending logic here (e.g., using SMTP)
    print(f"Email sent to {details.applicant_email} and {details.interviewer_email} with content: {email_content}")