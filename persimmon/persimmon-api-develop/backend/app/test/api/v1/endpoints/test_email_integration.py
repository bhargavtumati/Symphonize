import pytest
import io
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.helpers.firebase_helper import verify_firebase_token

client = TestClient(app)

def mock_verify_firebase_token():
    return {"user_id": "111", "email": "gunda.charanreddy@tekworks.in"}

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

@patch("app.models.company.Company.get_by_domain")
@patch("app.models.job.Job.get_by_code")
@patch("app.models.recruiter.Recruiter.get_by_email_id")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.helpers.email_helper.render_email_variables")
@patch("sib_api_v3_sdk.TransactionalEmailsApi.send_transac_email")
def test_send_email_success_with_brevo(
    mock_send_transac_email, 
    mock_render_email_variables, 
    mock_get_credentials, 
    mock_get_recruiter, 
    mock_get_job, 
    mock_get_company
):
    mock_get_company.return_value = MagicMock(id=1, domain="tekworks.in")
    mock_get_job.return_value = MagicMock(id=1, title="Software Engineer")
    mock_get_recruiter.return_value = MagicMock(id=1, email="gunda.charanreddy@tekworks.in")
    mock_get_credentials.return_value = MagicMock(credentials={"credentials": [{"service_type": "brevo", "api_key": "test_api_key"}]})
    mock_render_email_variables.return_value = ("Test Body", "Test Subject")
    mock_send_transac_email.return_value = {"status": 200, "message": "Email sent successfully!"}

    response = client.post(
        "api/v1/integration/email/brevo/send",
        data={
            "job_code": "JOB123",
            "to_email": "candidate@example.com",
            "from_email": "gunda.charanreddy@tekworks.in",
            "subject": "Interview Invitation",
            "body": "Hello, please join the interview"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Email processing completed"
    assert response.json()["success_count"] == 1
    assert response.json()["failure_count"] == 0
    
    mock_get_company.assert_called_once()
    mock_get_job.assert_called_once()
    mock_get_recruiter.assert_called_once()
    mock_get_credentials.assert_called_once()
    mock_render_email_variables.assert_called()
    mock_send_transac_email.assert_called()


@patch("app.models.company.Company.get_by_domain")
@patch("app.models.job.Job.get_by_code")
@patch("app.models.recruiter.Recruiter.get_by_email_id")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.helpers.email_helper.render_email_variables")
@patch("sib_api_v3_sdk.TransactionalEmailsApi.send_transac_email")
def test_send_email_failure_with_brevo(
    mock_send_transac_email, 
    mock_render_email_variables, 
    mock_get_credentials, 
    mock_get_recruiter, 
    mock_get_job, 
    mock_get_company
):
    mock_get_company.return_value = MagicMock(id=1, domain="tekworks.in")
    mock_get_job.return_value = MagicMock(id=1, title="Software Engineer")
    mock_get_recruiter.return_value = MagicMock(id=1, email="gunda.charanreddy@tekworks.in")
    mock_get_credentials.return_value = MagicMock(credentials={"credentials": [{"service_type": "brevo", "api_key": "test_api_key"}]})
    mock_render_email_variables.return_value = ("Test Body", "Test Subject")
    mock_send_transac_email.side_effect = HTTPException(status_code=401, detail="Invalid API key")

    response = client.post(
        "api/v1/integration/email/brevo/send",
        data={
            "job_code": "JOB123",
            "to_email": "candidate@example.com",
            "from_email": "gunda.charanreddy@tekworks.in",
            "subject": "Interview Invitation",
            "body": "Hello, please join the interview"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Email processing completed with some failures"
    assert response.json()["success_count"] == 0
    assert response.json()["failure_count"] == 1
    
    mock_get_company.assert_called_once()
    mock_get_job.assert_called_once()
    mock_get_recruiter.assert_called_once()
    mock_get_credentials.assert_called_once()
    mock_render_email_variables.assert_called()
    mock_send_transac_email.assert_called()


@patch("app.models.company.Company.get_by_domain")
@patch("app.models.job.Job.get_by_code")
@patch("app.models.recruiter.Recruiter.get_by_email_id")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.helpers.email_helper.render_email_variables")
@patch("sendgrid.SendGridAPIClient.send")
def test_send_email_success_with_sendgrid(
    mock_send, 
    mock_render_email_variables, 
    mock_get_credentials, 
    mock_get_recruiter, 
    mock_get_job, 
    mock_get_company
):
    mock_get_company.return_value = MagicMock(id=1, domain="tekworks.in")
    mock_get_job.return_value = MagicMock(id=1, title="Software Engineer")
    mock_get_recruiter.return_value = MagicMock(id=1, email="gunda.charanreddy@tekworks.in")
    mock_get_credentials.return_value = MagicMock(credentials={"credentials": [{"service_type": "sendgrid", "api_key": "test_api_key"}]})
    mock_render_email_variables.return_value = ("Test Body", "Test Subject")
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_send.return_value = mock_response

    response = client.post(
        "api/v1/integration/email/sendgrid/send",
        data={
            "job_code": "JOB123",
            "to_email": "candidate@example.com",
            "from_email": "gunda.charanreddy@tekworks.in",
            "subject": "Interview Invitation",
            "body": "Hello, please join the interview"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Email processing completed"
    assert response.json()["success_count"] == 1
    assert response.json()["failure_count"] == 0
    
    mock_get_company.assert_called_once()
    mock_get_job.assert_called_once()
    mock_get_recruiter.assert_called_once()
    mock_get_credentials.assert_called_once()
    mock_render_email_variables.assert_called_once()
    mock_send.assert_called_once()


@patch("app.models.company.Company.get_by_domain")
@patch("app.models.job.Job.get_by_code")
@patch("app.models.recruiter.Recruiter.get_by_email_id")
@patch("app.models.integration.Integration.get_credentials")
def test_send_email_with_invalid_service(
    mock_get_credentials, 
    mock_get_recruiter, 
    mock_get_job, 
    mock_get_company
):
    mock_get_company.return_value = MagicMock(id=1, domain="tekworks.in")
    mock_get_job.return_value = MagicMock(id=1, title="Software Engineer")
    mock_get_recruiter.return_value = MagicMock(id=1, email="gunda.charanreddy@tekworks.in")
    mock_get_credentials.return_value = MagicMock(credentials={"credentials": [{"service_type": "brevo", "api_key": "test_api_key"}]})

    response = client.post(
        "api/v1/integration/email/mandrill/send",
        data={
            "job_code": "JOB123",
            "to_email": "candidate@example.com",
            "from_email": "gunda.charanreddy@tekworks.in",
            "subject": "Interview Invitation",
            "body": "Hello, please join the interview"
        }
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'mandrill credentials not found'
    
    mock_get_company.assert_called_once()
    mock_get_job.assert_called_once()
    mock_get_recruiter.assert_called_once()
    mock_get_credentials.assert_called_once()


@patch("app.models.company.Company.get_by_domain")
@patch("app.models.job.Job.get_by_code")
@patch("app.models.recruiter.Recruiter.get_by_email_id")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.helpers.email_helper.render_email_variables")
@patch("sib_api_v3_sdk.TransactionalEmailsApi.send_transac_email")
def test_send_email_with_attachments_for_multiple_candidates(
    mock_send_transac_email, 
    mock_render_email_variables, 
    mock_get_credentials, 
    mock_get_recruiter, 
    mock_get_job, 
    mock_get_company
):
    mock_get_company.return_value = MagicMock(id=1, domain="tekworks.in")
    mock_get_job.return_value = MagicMock(id=1, title="Software Engineer")
    mock_get_recruiter.return_value = MagicMock(id=1, email="gunda.charanreddy@tekworks.in")
    mock_get_credentials.return_value = MagicMock(credentials={"credentials": [{"service_type": "brevo", "api_key": "test_api_key"}]})
    mock_render_email_variables.return_value = ("Test Body", "Test Subject")
    mock_send_transac_email.return_value = {"status": 200, "message": "Email sent successfully!"}

    # Simulating file uploads
    file_1 = io.BytesIO(b"Dummy file content 1")
    file_2 = io.BytesIO(b"Dummy file content 2")
    
    response = client.post(
        "api/v1/integration/email/brevo/send",
        data={
            "job_code": "JOB123",
            "to_email": "candidate1@example.com, candidate2@example.com, candidate3@example.com",
            "from_email": "gunda.charanreddy@tekworks.in",
            "subject": "Interview Invitation",
            "body": "Hello, please join the interview"
        },
        files=[
            ("attachments", ("file1.txt", file_1, "text/plain")),
            ("attachments", ("file2.pdf", file_2, "application/pdf"))
        ]
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Email processing completed"
    assert response.json()["success_count"] == 3
    assert response.json()["failure_count"] == 0
    
    mock_get_company.assert_called()
    mock_get_job.assert_called()
    mock_get_recruiter.assert_called()
    mock_get_credentials.assert_called()
    mock_render_email_variables.assert_called()
    mock_send_transac_email.assert_called()


@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)


@patch("app.models.company.Company.get_by_domain")
@patch("app.models.integration.Integration.get_credentials", return_value=None)
@patch("app.models.integration.Integration.create", return_value=None)
@patch("app.helpers.email_helper.get_brevo_senders", return_value=None)
@patch("app.helpers.regex_helper.get_domain_from_email")
def test_create_email_integration(
    mock_get_domain_from_email,
    mock_get_brevo_senders,
    mock_create,
    mock_get_credentials,
    mock_get_by_domain
):
    """Test email integration for both Brevo and SendGrid"""

    mock_get_domain_from_email.return_value = "tekworks.in"
    mock_company = MagicMock(id=1, domain="tekworks.in")
    mock_get_by_domain.return_value = mock_company

    response = client.post(
        f"api/v1/integration/email/brevo",
        json={"api_key": "uxbvdhwbdhwdchclknbn"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == 201
    assert response.json()["message"] == "Email integration is successful"

    mock_get_by_domain.assert_called_once()
    mock_create.assert_called_once()
    mock_get_credentials.assert_called_once()
    mock_get_brevo_senders.assert_called_once()


@patch("app.models.integration.Integration.get_credentials")
@patch("app.helpers.email_helper.get_brevo_senders", return_value=None)
@patch("app.models.company.Company.get_by_domain")
@patch("app.helpers.db_helper.update_meta", return_value={"updated_by": "charan"})
def test_create_email_integration_to_update_api_key(
    mock_update_meta,
    mock_get_by_domain,
    mock_get_brevo_senders,
    mock_get_credentials,
):
    """Test email integration for both Brevo and SendGrid"""

    mock_company = MagicMock(id=1, domain="tekworks.in")
    mock_get_by_domain.return_value = mock_company

    mock_integration = MagicMock()
    mock_integration.credentials = {
        "credentials": [{"service_type": "brevo", "api_key": "hxvwxgvxgtwhwgx"}]
    }
    mock_integration.meta = {}

    mock_integration.update = MagicMock()

    mock_get_credentials.return_value = mock_integration

    response = client.post(
        "api/v1/integration/email/brevo",
        json={"api_key": "uxbvdhwbdhwdchclknbn"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == 201
    assert response.json()["message"] == "Email integration is successful"

    mock_get_by_domain.assert_called_once()
    mock_get_credentials.assert_called_once()
    mock_get_brevo_senders.assert_called_once()
    mock_update_meta.assert_called_once()

    mock_integration.update.assert_called_once()


@patch("app.helpers.regex_helper.get_domain_from_email", return_value=None)
def test_create_email_integration_invalid_domain(mock_get_domain_from_email):
    """Test error when email domain is invalid"""
    
    response = client.post(
        "api/v1/integration/email/brevo",
        json={"api_key": "test_api_key"},
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Domain is invalid"


@patch("app.models.company.Company.get_by_domain")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.helpers.regex_helper.get_domain_from_email")
def test_verify_integration_status_exists(
    mock_get_domain_from_email,
    mock_get_credentials,
    mock_get_by_domain
):
    """Test case when integration exists and matches the service type."""
    
    mock_get_domain_from_email.return_value = "tekworks.in"

    mock_company = MagicMock(id=1, domain="tekworks.in")
    mock_get_by_domain.return_value = mock_company

    mock_integration = MagicMock(credentials={
        "credentials": [{"service_type": "brevo", "api_key": "test_key"}]
    })
    mock_get_credentials.return_value = mock_integration

    response = client.get("api/v1/integration/email/brevo/verify-status")

    assert response.status_code == 200
    assert response.json() is True  


@patch("app.models.company.Company.get_by_domain")
@patch("app.models.integration.Integration.get_credentials", return_value=None)
@patch("app.helpers.regex_helper.get_domain_from_email")
def test_verify_integration_status_not_exists(
    mock_get_domain_from_email,
    mock_get_credentials,
    mock_get_by_domain
):
    """Test case when integration does not exist or service type does not match."""
    
    mock_get_domain_from_email.return_value = "tekworks.in"

    mock_company = MagicMock(id=1, domain="tekworks.in")
    mock_get_by_domain.return_value = mock_company

    response = client.get("api/v1/integration/email/sendgrid/verify-status")

    assert response.status_code == 200
    assert response.json() is False  
