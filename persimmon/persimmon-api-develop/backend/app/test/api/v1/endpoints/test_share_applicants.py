import os
import datetime
from uuid import uuid4

import jwt

import pytest

from unittest.mock import AsyncMock, patch, MagicMock

from fastapi.testclient import TestClient

from app.main import app  
from app.helpers.firebase_helper import verify_firebase_token

SECRET_KEY = os.getenv("SECRET_KEY")
VALID_UUID = str(uuid4())  
INVALID_UUID = "invalid-uuid"

client = TestClient(app=app)

@pytest.fixture(autouse=True)
def mock_dependencies():
    with patch("app.models.shared.Shared.create", return_value=None) as mock_create, \
         patch("app.models.job.Job.get_by_code", return_value=MagicMock(title="Software Engineer")) as mock_get_by_code, \
         patch("app.models.recruiter.Recruiter.get_by_email_id", return_value=MagicMock(full_name="charanreddy", designation="Python Developer")) as get_by_email_id,\
         patch("app.models.applicant.Applicant.get_missing_applicants", return_value=[]) as mock_get_missing_applicants, \
         patch("app.models.company.Company.get_by_domain", return_value=MagicMock(id=1, name="Tekworks")) as mock_get_company, \
         patch("app.models.integration.Integration.get_credentials", return_value=MagicMock(
            credentials={"credentials": [{"service_type": "brevo", "api_key": "mock_api_key"}, {"service_type": "sendgrid", "api_key": "mock_api_key"}]}
            )) as mock_get_integration, \
         patch("app.helpers.email_helper.send_email", return_value=None) as mock_send_email, \
         patch("app.helpers.email_helper.brevo_send_mail", return_value=None) as mock_brevo_email, \
         patch("app.helpers.email_helper.sendgrid_send_mail", return_value=None) as mock_sendgrid_email, \
         patch("app.helpers.regex_helper.get_domain_from_email", return_value="example.com") as mock_get_domain:
        yield {
            "mock_create": mock_create,
            "mock_get_by_code": mock_get_by_code,
            "mock_get_missing_applicants": mock_get_missing_applicants,
            "mock_get_company": mock_get_company,
            "mock_get_integration": mock_get_integration,
            "mock_send_email": mock_send_email,
            "mock_brevo_email": mock_brevo_email,
            "mock_sendgrid_email": mock_sendgrid_email,
            "mock_get_domain": mock_get_domain,
            "get_by_email_id": get_by_email_id
        }


def test_share_applicant_default_email(mock_dependencies):
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}    
    request_data = {
        "job_code": "J123",
        "recipient_emails": ["recipient@example.com"],
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": True,
        "email_type": "default",
        "sender": os.getenv("FROM_ADDRESS"),
        "redirect_url": "https://localhost:8080/share-applicants"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["message"] == "Shared Applicants Successfully"
    assert json_response["success_count"] == 1
    assert json_response['failure_count'] == 0
    mock_dependencies["mock_create"].assert_called_once()
    mock_dependencies["mock_get_by_code"].assert_called_once()
    mock_dependencies["mock_get_missing_applicants"].assert_called_once()
    mock_dependencies["mock_send_email"].assert_called_once()


def test_share_applicant_default_email_multiple_recipients(mock_dependencies):
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}    
    request_data = {
        "job_code": "J123",
        "recipient_emails": ["recipient@example.com", "recipient2@example.com"],
        "applicant_uuids": ["uuid1", "uuid2", "uuid3"],
        "hide_salary": True,
        "email_type": "default",
        "sender": os.getenv("FROM_ADDRESS"),
        "redirect_url": "https://localhost:8080/share-applicants"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["message"] == "Shared Applicants Successfully"
    assert json_response["success_count"] == 2
    assert json_response['failure_count'] == 0
    mock_dependencies["mock_create"].assert_called_once()
    mock_dependencies["mock_get_by_code"].assert_called_once()
    mock_dependencies["mock_get_missing_applicants"].assert_called_once()
    mock_dependencies["mock_send_email"].call_count == 2


def test_share_applicant_brevo(mock_dependencies):
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}
    request_data = {
        "job_code": "J123",
        "recipient_emails": ["recipient@example.com"],
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": False,
        "email_type": "brevo",
        "sender": "custom@example.com",
        "redirect_url": "https://localhost:8080/share-applicants"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["message"] == "Shared Applicants Successfully"
    assert json_response["success_count"] == 1
    assert json_response['failure_count'] == 0
    mock_dependencies["mock_brevo_email"].assert_called_once()
    mock_dependencies["mock_create"].assert_called_once()
    mock_dependencies["mock_get_by_code"].assert_called_once()
    mock_dependencies["mock_get_missing_applicants"].assert_called_once()
    mock_dependencies["mock_get_missing_applicants"].assert_called_once()
    mock_dependencies["mock_get_company"].assert_called()
    mock_dependencies["mock_get_integration"].assert_called_once()


def test_share_applicant_sendgrid(mock_dependencies):
    request_data = {
        "job_code": "J123",
        "recipient_emails": ["recipient@example.com"],
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": False,
        "email_type": "sendgrid",
        "sender": "custom@example.com",
        "redirect_url": "https://localhost:8080/share-applicants"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    assert response.status_code == 200
    json_response = response.json()
    assert response.json()["message"] == "Shared Applicants Successfully"
    assert json_response["success_count"] == 1
    assert json_response['failure_count'] == 0
    mock_dependencies["mock_sendgrid_email"].assert_called_once()
    mock_dependencies["mock_get_by_code"].assert_called_once()
    mock_dependencies["mock_get_missing_applicants"].assert_called_once()
    mock_dependencies["mock_get_missing_applicants"].assert_called_once()
    mock_dependencies["mock_get_company"].assert_called()
    mock_dependencies["mock_get_integration"].assert_called_once()


def test_share_applicant_invalid_email_type():
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}
    request_data = {
        "job_code": "J123",
        "recipient_emails": ["recipient@example.com"],
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": False,
        "email_type": "invalid_service",
        "sender": "custom@example.com",
        "redirect_url": "https://localhost:8080/share-applicants"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    assert response.status_code == 422


def test_share_applicant_company_not_found(mock_dependencies):
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}
    mock_dependencies['mock_get_company'].return_value = None
    request_data = {
        "job_code": "J123",
        "recipient_emails": ["recipient@example.com"],
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": False,
        "email_type": "brevo",
        "sender": "pytest@tekworks.in",
        "redirect_url": "https://localhost:8080/share-applicants"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Company details not found'


def test_share_applicant_invalid_sender(mock_dependencies):
    mock_dependencies['mock_get_company'].return_value = None
    request_data = {
        "job_code": "J123",
        "recipient_emails": ["recipient@example.com"],
        "applicant_uuids": ["uuid1", "uuid2"],
        "hide_salary": False,
        "email_type": "default",
        "sender": "pytest@tekworks.in",
        "redirect_url": "https://localhost:8080/share-applicants"
    }
    response = client.post("api/v1/share/applicants", json=request_data)
    print(response.json())
    assert response.status_code == 500
    assert response.json()['detail'] == 'Failed to Share Applicants: The sender address is not authorized'


@patch("app.models.job.Job.get_by_code", return_value = MagicMock(enhanced_description={"skills":[], "availability":45}))
def test_verify_email(mock_get_by_code):
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}
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
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}
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


filters_payload = {
  "filters": {
    "industry_type": [
      {
        "max": 12,
        "min": 10,
        "name": "IT Services and IT Consulting",
        "pref": "Must have"
      }
    ],
    "remuneration": {
      "name": "Salary Range",
      "min": 15,
      "max": 18
    },
    "skills": [
      {
        "name": "Java",
        "pref": "Must have",
        "value": 10,
        "rating": 10
      },
      {
        "name": "Spring Boot",
        "pref": "Must have",
        "value": 10,
        "rating": 10
      }
    ],
    "responsibilities": [
      "Design applications",
      "Develop applications",
      "Maintain applications",
      "Gather requirements",
      "Collaborate with team",
    ],
    "availability": {
      "name": "Can Join in",
      "value": 0
    },
    "workmode": {
      "value": "Any"
    },
    "location": {
      "first_priority": "Hyderabad",
      "second_priority": "Any"
    },
    "soft_skills": [
      {
        "name": "Problem-solving",
        "pref": "Must have",
        "rating": 2
      },
      {
        "name": "Mentoring",
        "pref": "Must have",
        "rating": 2
      }
    ],
    "transition_behaviour": [
      {
        "name": "Avg. Duration in Previous Companies",
        "preference": "Good to have",
        "value": 0
      }
    ]
  }
}


@patch("app.models.shared.Shared.get_by_uuid")
@patch("app.helpers.solr_helper.query_solr_with_filters", new_callable=AsyncMock)
def test_get_applicants(
    mock_query_solr_with_filters,
    mock_get_by_uuid
):
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}
    mock_get_by_uuid.return_value = MagicMock(details=["ubxhuvcquvuvyc", "hjcvhvwvjvwivwy"])
    mock_query_solr_with_filters.return_value = {"response": {"docs": []}}
    payload = {
        "token_uuid": "hvcvcxgqvcv", 
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7) 
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm="HS256")
    headers = {
    "Authorization": f"Bearer {token}"
    }
    response = client.post("api/v1/share/applicants/filter", json=filters_payload, headers=headers)
    assert response.status_code == 200
    assert "solr_response" in response.json()
    mock_get_by_uuid.assert_called_once()


@patch("app.models.shared.Shared.get_by_uuid")
@patch("app.helpers.solr_helper.query_solr_with_filters", new_callable=AsyncMock)
def test_get_applicants(
    mock_query_solr_with_filters,
    mock_get_by_uuid
):
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}
    mock_get_by_uuid.return_value = MagicMock(details=["ubxhuvcquvuvyc", "hjcvhvwvjvwivwy"])
    mock_query_solr_with_filters.return_value = {"response": {"docs": []}}
    payload = {
        "token_uuid": "mock-token-uuid",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm="HS256")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.post("/api/v1/share/applicants/filter?page=1", json=filters_payload, headers=headers)
    assert response.status_code == 200, response.text
    assert "solr_response" in response.json()
    mock_get_by_uuid.assert_called_once()
    mock_query_solr_with_filters.assert_called_once()



@patch("app.models.applicant.Applicant.get_by_uuid")
@patch("app.helpers.date_helper.convert_epoch_to_utc", return_value="2024-01-01T12:00:00Z")
def test_get_applicant_success(
    mock_convert_epoch,
    mock_get_by_uuid
):
    """Test retrieving an applicant successfully"""
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}
    mock_get_by_uuid.return_value = MagicMock(
        details={"name": "John Doe", "email": "john@example.com"},
        stage_uuid="stage-123",
        job_id="job-456",
        uuid=VALID_UUID,
        meta={"audit": {"created_at": 1704067200}} 
    )
    payload = {
        "token_uuid": "mock-token-uuid",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/applicants/{VALID_UUID}", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Applicant details retrieved successfully"
    assert response.json()["data"]["details"]["applied_date"] == "2024-01-01T12:00:00Z"
    mock_get_by_uuid.assert_called_once()
    mock_convert_epoch.assert_called_once()


def test_get_applicant_invalid_uuid():
    """Test when an invalid UUID is provided"""
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}
    payload = {
        "token_uuid": "mock-token-uuid",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/applicants/{INVALID_UUID}", headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or Required UUID"


@patch("app.models.applicant.Applicant.get_by_uuid", return_value=None)
def test_get_applicant_not_found(mock_get_by_uuid):
    """Test when applicant is not found"""
    app.dependency_overrides[verify_firebase_token] = lambda: {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}
    payload = {
        "token_uuid": "mock-token-uuid",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/applicants/{VALID_UUID}", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Applicant not found"
    mock_get_by_uuid.assert_called_once()