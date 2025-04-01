from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.helpers.firebase_helper import verify_firebase_token
import uuid

client = TestClient(app)

# Set up the dependency override globally
def mock_verify_firebase_token():
    return {"user_id": "111", "email": "bhargav.tumati@tekworks.in"}

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

@patch("app.models.company.Company.get_by_domain")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.helpers.wati_helper.send_whatsapp_message_via_wati")
def test_send_bulk_whatsapp_messages_success(
    mock_send_message_via_wati, 
    mock_get_credentials, 
    mock_get_by_domain
):
    # Generate a valid UUID for the applicant
    applicant_uuid = str(uuid.uuid4())  # e.g., "550e8400-e29b-41d4-a716-446655440000"

    # Mock return values
    mock_get_by_domain.return_value = MagicMock(id=1, domain="tekworks.in")
    mock_integration = MagicMock()
    mock_integration.credentials = {
        "credentials": [{"service_type": "wati", "wati_api_token": "test_api_key", "wati_api_endpoint": "test_endpoint"}]
    }

    mock_get_credentials.return_value = mock_integration


    # Payload with valid UUID
    payload = {
        "request": {
            "applicant_uuids": [applicant_uuid],  # Use valid UUID
            "template_name": "greeting",
            "body_params": [ "name", "yop" ]
        },
        
        "params": [
            {"name": "name", "value": "full_name"},
            {"name": "yop", "value": "date_of_birth"}
        ]
    }

    # Send request with correct route and payload
    response = client.post(
        "/api/v1/wati/send-whatsapp",  # Removed trailing slash
        json=payload,
        headers={"Authorization": "Bearer mock_token"}
    )

    # Debug output
    print(f"Payload sent: {payload}")
    print(f"Response: {response.status_code} - {response.text}")

    # Assertions
    assert response.status_code == 200


    # Verify mocks were called
    mock_get_by_domain.assert_called_once()
    mock_get_credentials.assert_called_once()
    mock_send_message_via_wati.assert_called_once()



@patch("app.models.company.Company.get_by_domain")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.api.v1.endpoints.wati.get_template_body_params")
@patch("app.helpers.applicant_helper.get_applicants_data")
def test_send_bulk_whatsapp_messages_missing_template(
    mock_get_applicants_data, mock_get_template_body_params, mock_get_credentials, mock_get_by_domain
):
    """Test failure when template_name is missing"""
    applicant_uuid = str(uuid.uuid4())

    mock_get_by_domain.return_value = MagicMock(id=1, domain="tekworks.in")
    mock_get_template_body_params.return_value = {"name": "full_name", "yop": "date_of_birth"}
    mock_integration = MagicMock()
    mock_integration.credentials = {
        "credentials": [{"service_type": "wati", "wati_api_token": "test_api_key", "wati_api_endpoint": "test_endpoint"}]
    }
    mock_get_credentials.return_value = mock_integration
    mock_get_applicants_data.return_value = {applicant_uuid: {"id": applicant_uuid, "phone_number": "+911234567890", "name": "John Doe"}}

    payload = {
        "request": {
            "applicant_uuids": [applicant_uuid]  # Missing "template_name"
        },
        "params": [
            {"name": "name", "value": "full_name"},
            {"name": "yop", "value": "date_of_birth"}
        ]
    }

    response = client.post("/api/v1/wati/send-whatsapp", json=payload, headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 422  # Unprocessable Entity
    assert "template_name" in response.text


@patch("app.models.company.Company.get_by_domain")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.api.v1.endpoints.wati.get_template_body_params")
@patch("app.helpers.applicant_helper.get_applicants_data")
def test_send_bulk_whatsapp_messages_invalid_uuid(
    mock_get_applicants_data, mock_get_template_body_params, mock_get_credentials, mock_get_by_domain
):
    """Test failure when UUID format is incorrect"""
    mock_get_by_domain.return_value = MagicMock(id=1, domain="tekworks.in")
    mock_get_template_body_params.return_value = {"name": "full_name", "yop": "date_of_birth"}
    mock_integration = MagicMock()
    mock_integration.credentials = {
        "credentials": [{"service_type": "wati", "wati_api_token": "test_api_key", "wati_api_endpoint": "test_endpoint"}]
    }
    mock_get_credentials.return_value = mock_integration
    mock_get_applicants_data.return_value = {}

    payload = {
        "request": {
            "applicant_uuids": ["invalid-uuid"],  # Invalid UUID format
            "template_name": "greeting",
            "body_params": [ "name", "yop" ]
        },
        "params": [
            {"name": "name", "value": "full_name"},
            {"name": "yop", "value": "date_of_birth"}
        ]
    }

    response = client.post("/api/v1/wati/send-whatsapp", json=payload, headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 422  # Unprocessed entity
    


@patch("app.models.company.Company.get_by_domain")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.api.v1.endpoints.wati.get_template_body_params")
@patch("app.helpers.applicant_helper.get_applicants_data")
def test_send_bulk_whatsapp_messages_no_applicants_found(
    mock_get_applicants_data, mock_get_template_body_params, mock_get_credentials, mock_get_by_domain
):
    """Test failure when no applicants are found"""
    applicant_uuid = str(uuid.uuid4())

    mock_get_by_domain.return_value = MagicMock(id=1, domain="tekworks.in")
    mock_get_template_body_params.return_value = {"name": "full_name", "yop": "date_of_birth"}
    mock_integration = MagicMock()
    mock_integration.credentials = {
        "credentials": [{"service_type": "wati", "wati_api_token": "test_api_key", "wati_api_endpoint": "test_endpoint"}]
    }
    mock_get_credentials.return_value = mock_integration
    mock_get_applicants_data.return_value = {}  # No applicants

    payload = {
        "request": {
            "applicant_uuids": [applicant_uuid],
            "template_name": "greeting",
            "body_params": [ "name", "yop" ]
        },
        "params": [
            {"name": "name", "value": "full_name"},
            {"name": "yop", "value": "date_of_birth"}
        ]
    }

    response = client.post("/api/v1/wati/send-whatsapp", json=payload, headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 404  # Not Found
    assert "No applicants found" in response.text


@patch("app.models.company.Company.get_by_domain")
@patch("app.models.integration.Integration.get_credentials")
@patch("app.api.v1.endpoints.wati.get_template_body_params")
@patch("app.helpers.applicant_helper.get_applicants_data")
def test_send_bulk_whatsapp_messages_missing_wati_token(
    mock_get_applicants_data, mock_get_template_body_params, mock_get_credentials, mock_get_by_domain
):
    """Test failure when WATI API token is missing"""
    applicant_uuid = str(uuid.uuid4())

    mock_get_by_domain.return_value = MagicMock(id=1, domain="tekworks.in")
    mock_get_template_body_params.return_value = {"name": "full_name", "yop": "date_of_birth"}
    mock_integration = MagicMock()
    mock_integration.credentials = {
        "credentials": [{"service_type": "wati"}]  # Missing API token
    }
    mock_get_credentials.return_value = mock_integration
    mock_get_applicants_data.return_value = {applicant_uuid: {"id": applicant_uuid, "phone_number": "+911234567890", "name": "John Doe"}}

    payload = {
        "request": {
            "applicant_uuids": [applicant_uuid],
            "template_name": "greeting",
            "body_params": [ "name", "yop" ]
        },
        "params": [
            {"name": "name", "value": "full_name"},
            {"name": "yop", "value": "date_of_birth"}
        ]
    }

    response = client.post("/api/v1/wati/send-whatsapp", json=payload, headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 404  #Not found
    assert "wati api token not found" in response.text


@patch("app.models.company.Company.get_by_domain", return_value=None)
def test_send_bulk_whatsapp_messages_company_not_found(mock_get_by_domain):
    """Test failure when company domain is not found"""
    payload = {
        "request": {
            "applicant_uuids": [str(uuid.uuid4())],
            "template_name": "greeting",
            "body_params": [ "name", "yop" ]
        },
        "params": [
            {"name": "name", "value": "full_name"},
            {"name": "yop", "value": "date_of_birth"}
        ]
    }

    response = client.post("/api/v1/wati/send-whatsapp", json=payload, headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 404
    assert "Company details not found" in response.text