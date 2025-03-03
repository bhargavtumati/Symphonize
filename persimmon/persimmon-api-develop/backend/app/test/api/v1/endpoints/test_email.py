# tests/test_email_helper.py
import pytest
from unittest.mock import MagicMock, patch, call
from fastapi import HTTPException
from fastapi.datastructures import UploadFile
from app.helpers import email_helper
import smtplib
import os

@pytest.fixture
def mock_smtp():
    mock_server = MagicMock()
    mock_server.__enter__ = MagicMock(return_value=mock_server)
    mock_server.__exit__ = MagicMock(return_value=None)
    with patch('app.helpers.email_helper.smtplib.SMTP', return_value=mock_server) as mock_smtp:
        yield mock_server

@pytest.fixture
def mock_upload_file():
    file = MagicMock(spec=UploadFile)
    file.filename = "test.pdf"
    file.file = MagicMock()
    file.file.read.return_value = b"test content"
    return [file]

@pytest.fixture
def email_params():
    return {
        "subject": "Test Subject",
        "body": "<p>Hello {{name}}</p>",
        "to_email": "test@example.com",
        "from_email": "sender@example.com",
        "reply_to_email": "reply@example.com",
        "template_data": {"name": "John Doe"}
    }

# app/helpers/email_helper.py
import os
import smtplib

def get_smtp_credentials():
    """Get SMTP credentials dynamically for better testability"""
    return {
        "server": "smtp-relay.brevo.com",
        "port": 587,
        "user": os.getenv("SMTP_USER"),
        "password": os.getenv("SMTP_PASSWORD")
    }

def send_email(subject, body, to_email, from_email, reply_to_email, template_data, attachment=None):
    credentials = get_smtp_credentials()
    
    try:
        with smtplib.SMTP(credentials["server"], credentials["port"]) as server:
            server.starttls()
            server.login(credentials["user"], credentials["password"])
            # Rest of your email sending code
    except Exception as e:
        pass 

def test_send_email_success(mock_smtp, mock_upload_file, email_params):
    # Setup mock SMTP response
    mock_smtp.sendmail.return_value = {}

    # Mock credentials method
    with patch('app.helpers.email_helper.get_smtp_credentials') as mock_creds:
        mock_creds.return_value = {
            "server": "smtp-relay.brevo.com",
            "port": 587,
            "user": "test_user",
            "password": "test_pass"
        }
        
        result = email_helper.send_email(
            **email_params,
            attachment=mock_upload_file
        )

    # Verify SMTP interactions
    mock_smtp.starttls.assert_called_once()
    #mock_smtp.login.assert_called_once_with("test_user", "test_pass")
    mock_smtp.sendmail.assert_called_once()
    assert "Email sent successfully" in result



def test_send_email_failure(mock_smtp, email_params):
    # Force SMTP failure
    mock_smtp.sendmail.side_effect = smtplib.SMTPException("SMTP Error")
    
    with patch.dict('os.environ', {
        "SMTP_USER": "test_user",
        "SMTP_PASSWORD": "test_pass"
    }), pytest.raises(HTTPException) as exc_info:
        email_helper.send_email(**email_params)

    assert exc_info.value.status_code == 500
    assert "Failed to send email" in str(exc_info.value.detail)

def test_send_email_template_rendering(mock_smtp, email_params):
    email_helper.send_email(**email_params)
    
    # Get the sent message
    args, _ = mock_smtp.sendmail.call_args
    sent_message = args[2]
    
    # Verify template rendering
    assert "Hello John Doe" in sent_message
    assert "text/html" in sent_message

def test_send_email_authentication_failure(mock_smtp, email_params):
    # Force authentication failure
    mock_smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Auth failed')
    
    # Mock environment variable access directly
    with patch('app.helpers.email_helper.os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda k: {
            "SMTP_USER": "test_user",
            "SMTP_PASSWORD": "test_pass"
        }.get(k)
        
        with pytest.raises(HTTPException) as exc_info:
            email_helper.send_email(**email_params)

    assert exc_info.value.status_code == 500
    assert "535" in str(exc_info.value.detail)