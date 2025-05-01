from fastapi import status
from fastapi.testclient import TestClient

from unittest.mock import MagicMock, patch

from app.main import app
from app.helpers.firebase_helper import verify_firebase_token
from app.api.v1.endpoints.meta_data import ALLOWED_TYPES

client = TestClient(app)

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"
    }


@patch("app.models.master_data.MasterData.get_all_by_type")
def test_get_metadata_success(mock_get_all_by_type):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

    expected_data = ["Java Developer", "Python Developer", "DevOps Engineer"]
    mock_get_all_by_type.return_value = [(title,) for title in expected_data]

    response = client.get("/api/v1/metadata/job-title")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"] == expected_data
    assert mock_get_all_by_type.call_count == 1


def test_get_metadata_with_invalid_path_param():
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.get("/api/v1/metadata/designation")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"Invalid path parameter type. Allowed values are: {ALLOWED_TYPES}"


@patch("app.models.master_data.MasterData.get_all_by_type")
def test_get_metadata_database_error(mock_get_all_by_type):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

    mock_get_all_by_type.side_effect = Exception("Database error")

    response = client.get("/api/v1/metadata/job-title")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error" in response.json()["detail"]
    assert mock_get_all_by_type.call_count == 1


@patch("app.models.master_data.MasterData.get_existing_record", return_value=None)
@patch("app.models.master_data.MasterData.create", return_value=None)
@patch("app.models.master_data.MasterData.get_all_by_type")
def test_insert_metadata_by_type_success(
    mock_get_all_by_type,
    mock_create, 
    mock_get_existing_record
):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

    expected_data = ["Java Developer", "Python Developer", "DevOps Engineer"]
    mock_get_all_by_type.return_value = [(title,) for title in expected_data]

    response = client.post("/api/v1/metadata/job-title", json={"name": "Java Developer"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "job title added successfully"
    assert response.json()["data"] == expected_data

    mock_create.assert_called_once()
    mock_get_existing_record.assert_called_once()
    mock_get_all_by_type.called_once()  


@patch("app.models.master_data.MasterData.get_existing_record")
def test_insert_metadata_by_type_duplicate_insertion(mock_get_existing_record):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

    mock_get_existing_record.return_value = MagicMock(name={"Python Developer"}, type="job title")
    
    response = client.post("/api/v1/metadata/job-title", json={"name": "Java Developer"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "job title already exists"
    assert mock_get_existing_record.call_count == 1


def test_insert_metadata_by_type_with_invalid_path_param():
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

    response = client.post("/api/v1/metadata/designation", json={"name": "Java Developer"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == f"Invalid path parameter type. Allowed values are: {ALLOWED_TYPES}"


def test_insert_metadata_by_type_with_empty_payload():
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

    response = client.post("/api/v1/metadata/job-title", json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@patch("app.models.master_data.MasterData.get_existing_record")
def test_insert_metadata_by_type_duplicate_insertion(mock_get_existing_record):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

    mock_get_existing_record.side_effect = Exception("Database Error")
    
    response = client.post("/api/v1/metadata/job-title", json={"name": "Java Developer"})

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database Error" in response.json()["detail"] 
    assert mock_get_existing_record.call_count == 1