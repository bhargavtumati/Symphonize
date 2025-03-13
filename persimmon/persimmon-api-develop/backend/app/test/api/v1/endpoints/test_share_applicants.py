import os
import datetime
import pytest
import jwt

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app  
from app.helpers.firebase_helper import verify_firebase_token

SECRET_KEY = os.getenv("SECRET_KEY")

client = TestClient(app=app)

app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}    

@pytest.fixture
def mock_dependencies():
    with patch("app.models.shared.Shared.create", return_value=None) as mock_create, \
         patch("app.models.company.Company.get_by_domain", return_value=MagicMock(id=1)) as mock_get_company, \
         patch("app.models.integration.Integration.get_credentials", return_value=MagicMock(
            credentials={"credentials": [{"service_type": "brevo", "api_key": "mock_api_key"}, {"service_type": "sendgrid", "api_key": "mock_api_key"}]}
            )) as mock_get_integration, \
         patch("app.helpers.email_helper.send_email", return_value=None) as mock_send_email, \
         patch("app.helpers.email_helper.brevo_send_mail", return_value=None) as mock_brevo_email, \
         patch("app.helpers.email_helper.sendgrid_send_mail", return_value=None) as mock_sendgrid_email, \
         patch("app.helpers.regex_helper.get_domain_from_email", return_value="example.com") as mock_get_domain:
        yield {
            "mock_create": mock_create,
            "mock_get_company": mock_get_company,
            "mock_get_integration": mock_get_integration,
            "mock_send_email": mock_send_email,
            "mock_brevo_email": mock_brevo_email,
            "mock_sendgrid_email": mock_sendgrid_email,
            "mock_get_domain": mock_get_domain,
        }


def test_share_applicant_default_email(mock_dependencies):
    request_data = {
        "job_code": "J123",
        "job_title": "Software Engineer",
        "recipient_email": "recipient@example.com",
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": True,
        "email_type": "default",
        "sender": os.getenv("FROM_ADDRESS")
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Applicants Shared Successfully"
    mock_dependencies["mock_send_email"].assert_called_once()


def test_share_applicant_brevo(mock_dependencies):
    request_data = {
        "job_code": "J123",
        "job_title": "Software Engineer",
        "recipient_email": "recipient@example.com",
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": False,
        "email_type": "brevo",
        "sender": "custom@example.com"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Applicants Shared Successfully"
    mock_dependencies["mock_brevo_email"].assert_called_once()

def test_share_applicant_sendgrid(mock_dependencies):
    request_data = {
        "job_code": "J123",
        "job_title": "Software Engineer",
        "recipient_email": "recipient@example.com",
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": False,
        "email_type": "sendgrid",
        "sender": "custom@example.com"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Applicants Shared Successfully"
    mock_dependencies["mock_sendgrid_email"].assert_called_once()


def test_share_applicant_invalid_email_type():
    request_data = {
        "job_code": "J123",
        "job_title": "Software Engineer",
        "recipient_email": "recipient@example.com",
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": False,
        "email_type": "invalid_service",
        "sender": "custom@example.com"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    assert response.status_code == 422


def test_share_applicant_company_not_found(mock_dependencies):
    mock_dependencies['mock_get_company'].return_value = None
    request_data = {
        "job_code": "J123",
        "job_title": "Software Engineer",
        "recipient_email": "recipient@example.com",
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": False,
        "email_type": "brevo",
        "sender": "pytest@tekworks.in"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Company details not found'


def test_share_applicant_invalid_sender(mock_dependencies):
    mock_dependencies['mock_get_company'].return_value = None
    request_data = {
        "job_code": "J123",
        "job_title": "Software Engineer",
        "recipient_email": "recipient@example.com",
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": False,
        "email_type": "default",
        "sender": "pytest@tekworks.in"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    assert response.status_code == 500
    assert response.json()['detail'] == 'Failed to Share Applicants: The sender address is not authorized'


@patch("app.models.job.Job.get_by_code", return_value = MagicMock(enhanced_description={"skills":[], "availability":45}))
def test_verify_email(mock_get_by_code):
    payload = {
        "jc": "J123",
        "jt": "Software Engineer",
        "re": "recipient@tekworks.in",
        "token_uuid": "hvcvcxgqvcv", 
        "count": 5,
        "hs": 0,
        "se": "pytest@tekworks.in",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7) 
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm="HS256")
    headers = {
    "Authorization": f"Bearer {token}"
    }
    response = client.get("api/v1/share/applicants/details", headers=headers)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['message'] == 'Access granted'

    mock_get_by_code.assert_called_once()


def test_verify_email_with_no_token():
    payload = {
        "jc": "J123",
        "jt": "Software Engineer",
        "re": "recipient@tekworks.in",
        "token_uuid": "hvcvcxgqvcv", 
        "count": 5,
        "hs": 0,
        "se": "pytest@tekworks.in",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7) 
    }
    response = client.get("api/v1/share/applicants/details")
    response_data = response.json()
    assert response.status_code == 401
    assert response_data['detail'] == 'Authorization header missing'


def test_verify_email_with_no_token():
    payload = {
        "jc": "J123",
        "jt": "Software Engineer",
        "re": "recipient@tekworks.in",
        "token_uuid": "hvcvcxgqvcv", 
        "count": 5,
        "hs": 0,
        "se": "pytest@tekworks.in",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7) 
    }
    response = client.get("api/v1/share/applicants/details")
    response_data = response.json()
    assert response.status_code == 401
    assert response_data['detail'] == 'Authorization header missing'
