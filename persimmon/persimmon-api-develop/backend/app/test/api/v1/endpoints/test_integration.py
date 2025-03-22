import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app  
from app.helpers.firebase_helper import verify_firebase_token

client = TestClient(app)

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "test@example.com"
    }

@patch("app.models.company.Company.get_by_domain")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.models.integration.Integration.create")
@patch("app.models.integration.Integration.update")
@patch("app.helpers.regex_helper.get_domain_from_email")
@patch("app.helpers.zoom_helper.get_access_token")
@patch("app.helpers.db_helper.update_meta")
def test_create_integration_success(
    mock_update_meta,
    mock_get_access_token,
    mock_get_domain_from_email,
    mock_integration_update,
    mock_integration_create,
    mock_get_credentials,
    mock_get_by_domain,
):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    # Mock token dependency
    token = mock_verify_firebase_token()
    
    # Mocking helper function responses
    mock_get_domain_from_email.return_value = "example.com"
    mock_get_by_domain.return_value = MagicMock(id=1)
    mock_get_credentials.return_value = None
    
    mock_get_access_token.return_value = {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "expires_in": 3600,
    }
    
    # Test request payload
    request_data = {
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "redirect_uri": "https://mock-redirect.com",
        "code": "mock_auth_code",
    }
    
    response = client.post("api/v1/integration/zoom", json=request_data, headers={"Authorization": "Bearer mock_token"})
    
    assert response.json()["status"] == 201
    assert response.json()["message"] == "Zoom integration is successful"
    
    # Assert function calls
    mock_get_domain_from_email.assert_called_once()
    mock_get_by_domain.assert_called_once()
    mock_get_access_token.assert_called_once()
    mock_integration_create.assert_called_once()
    mock_integration_update.assert_not_called()

@patch("app.models.company.Company.get_by_domain")
@patch("app.helpers.regex_helper.get_domain_from_email")
def test_create_integration_invalid_domain(mock_get_domain_from_email, mock_get_by_domain):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_get_domain_from_email.return_value = None
    
    request_data = {
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "redirect_uri": "https://mock-redirect.com",
        "code": "mock_auth_code",
    }
    
    response = client.post("api/v1/integration/zoom", json=request_data, headers={"Authorization": "Bearer mock_token"})
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Domain is invalid"
    
    mock_get_domain_from_email.assert_called_once()
    mock_get_by_domain.assert_not_called()

@patch("app.models.company.Company.get_by_domain")
@patch("app.helpers.regex_helper.get_domain_from_email")
def test_verify_from_address_invalid_domain(mock_get_domain_from_email, mock_get_by_domain):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_get_domain_from_email.return_value = None
    
    response = client.get("api/v1/integration/email/verify-from-address", headers={"Authorization": "Bearer mock_token"})
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Domain is invalid"
    
    mock_get_domain_from_email.assert_called_once()
    mock_get_by_domain.assert_not_called()

@patch("app.models.integration.Integration.get_credentials")
@patch("app.models.company.Company.get_by_domain")
@patch("app.helpers.regex_helper.get_domain_from_email")
def test_verify_from_address_no_company_details(mock_get_domain_from_email, mock_get_by_domain, mock_get_credentials):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_get_domain_from_email.return_value = "example.com"
    mock_get_by_domain.return_value = None
    
    response = client.get("api/v1/integration/email/verify-from-address", headers={"Authorization": "Bearer mock_token"})
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Company details not found"
    
    mock_get_domain_from_email.assert_called_once()
    mock_get_by_domain.assert_called_once()
    mock_get_credentials.assert_not_called()

@patch("app.helpers.email_helper.get_sendgrid_senders", return_value=["test@example.com"])
@patch("app.models.integration.Integration.get_credentials")
@patch("app.models.company.Company.get_by_domain")
@patch("app.helpers.regex_helper.get_domain_from_email")
def test_verify_from_address_sendgrid_success(mock_get_domain_from_email, mock_get_by_domain, mock_get_credentials, mock_get_sendgrid_senders):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_get_domain_from_email.return_value = "example.com"
    mock_get_by_domain.return_value = MagicMock(id=1)
    mock_integration = MagicMock()
    mock_integration.credentials = {
        "credentials": [{"service_type": "sendgrid", "api_key": "mock_api_key"}]
    }
    mock_get_credentials.return_value = mock_integration
    
    response = client.get("api/v1/integration/email/verify-from-address", headers={"Authorization": "Bearer mock_token"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Your email found within the sendgrid integrated email service"
    assert response.json()["data"] is True
    
    mock_get_sendgrid_senders.assert_called_once_with(api_key="mock_api_key")

@patch("app.helpers.email_helper.get_brevo_senders", return_value=["test@example.com"])
@patch("app.models.integration.Integration.get_credentials")
@patch("app.models.company.Company.get_by_domain")
@patch("app.helpers.regex_helper.get_domain_from_email")
def test_verify_from_address_brevo_success(mock_get_domain_from_email, mock_get_by_domain, mock_get_credentials, mock_get_brevo_senders):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_get_domain_from_email.return_value = "example.com"
    mock_get_by_domain.return_value = MagicMock(id=1)
    mock_integration = MagicMock()
    mock_integration.credentials = {
        "credentials": [{"service_type": "brevo", "api_key": "mock_api_key"}]
    }
    mock_get_credentials.return_value = mock_integration
    
    response = client.get("api/v1/integration/email/verify-from-address", headers={"Authorization": "Bearer mock_token"})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Your email found within the brevo integrated email service"
    assert response.json()["data"] is True
    
    mock_get_brevo_senders.assert_called_once_with(api_key="mock_api_key")

@patch("app.models.integration.Integration.get_credentials")
@patch("app.models.company.Company.get_by_domain")
@patch("app.helpers.regex_helper.get_domain_from_email")
def test_verify_from_address_not_found(mock_get_domain_from_email, mock_get_by_domain, mock_get_credentials):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_get_domain_from_email.return_value = "example.com"
    mock_get_by_domain.return_value = MagicMock(id=1)
    mock_integration = MagicMock()
    mock_integration.credentials = {
        "credentials": [{"service_type": "sendgrid", "api_key": "mock_api_key"}]
    }
    mock_get_credentials.return_value = mock_integration
    
    with patch("app.helpers.email_helper.get_sendgrid_senders", return_value=[]) as mock_get_sendgrid_senders:
        response = client.get("api/v1/integration/email/verify-from-address", headers={"Authorization": "Bearer mock_token"})
    
        assert response.status_code == 200
        assert response.json()["message"] == "Your email not found within any integrated email service, please contact your administrator"
        assert response.json()["data"] is False
    
        mock_get_sendgrid_senders.assert_called_once_with(api_key="mock_api_key")
