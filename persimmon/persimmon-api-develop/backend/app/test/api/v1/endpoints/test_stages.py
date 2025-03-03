from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.helpers.firebase_helper import verify_firebase_token
from app.api.v1.endpoints.models.stages_model import StagesPartialUpdate
from app.models.stages import Stages
import uuid

client = TestClient(app)

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"
    }

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

def convert_uuids_to_strings(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, uuid.UUID):
                data[key] = str(value)
            elif isinstance(value, dict):
                convert_uuids_to_strings(value)
            elif isinstance(value, list):
                for item in value:
                    convert_uuids_to_strings(item)
    elif isinstance(data, list):
        for item in data:
            convert_uuids_to_strings(item)
    return data

@patch("app.models.stages.Stages.get_by_id")
def test_get_stages(mock_get_stages):
    mock_stages_instance = MagicMock()
    mock_stages_instance.stages = [
        {"uuid": "cd81dcf2-3d6a-492l-96k4-87782271079q", "name": "Interviewing"},
        {"uuid": "zm82dcf2-3h6a-492l-96k4-87782271079q", "name": "Deployed"},
        {"uuid": "md81dcf2-3d6a-492l-96k4-87782271079q", "name": "Rejected"}
    ]
    mock_get_stages.return_value = mock_stages_instance

    job_id = 1

    response = client.get(f"/api/v1/stages?job_id={job_id}")
    
    assert response.status_code == 200
    assert response.json() == {
        "stages": [
            {"uuid": "zm82dcf2-3h6a-492l-96k4-87782271079q", "name": "Deployed"},
            {"uuid": "md81dcf2-3d6a-492l-96k4-87782271079q", "name": "Rejected"}
        ],
        "message": "Stages list retrieved successfully",
        "status": 200
    }

@patch("app.models.job.Job.get_by_id")
@patch("app.models.stages.Stages.get_by_id")
@patch("app.helpers.stages_helper.check_immutable_objects")
@patch("app.helpers.solr_helper.update_solr_documents_partially", new_callable=AsyncMock)
@patch("app.models.applicant.Applicant.get_by_stage_uuid")
@patch("app.helpers.db_helper.update_meta")
def test_update_stages_success(
    mock_update_meta, mock_get_by_stage_uuid, mock_update_solr, 
    mock_check_immutable_objects, mock_get_job, mock_get_stages
):
    # Mock Job Data
    mock_job = MagicMock()
    mock_get_job.return_value = mock_job

    # Mock Existing Stages Data
    mock_stages_instance = MagicMock(spec=Stages)
    mock_stages_instance.stages = [
        {"uuid": "fbc5589e-9931-4d60-87ec-0c38bfd9c4e1", "name": "Shortlisted"},
        {"uuid": "7f32cc9e-e5fb-4cfb-9ae7-32e8d13648d1", "name": "Selected"},
        {"uuid": "52795e02-13e4-4452-9322-715001c58ff7", "name": "Rejected"}
    ]
    mock_get_stages.return_value = mock_stages_instance

    # Mock Stage Update Request
    mock_stages_partial_update = StagesPartialUpdate(
        stages=[
            {"uuid": "fbc5589e-9931-4d60-87ec-0c38bfd9c4e1", "name": "Shortlisted"},
            {"uuid": "7f32cc9e-e5fb-4cfb-9ae7-32e8d13648d1", "name": "Selected"},
            {"uuid": "52795e02-13e4-4452-9322-715001c58ff7", "name": "Rejected"},
            {"uuid": "c4d016ee-dfd5-4562-8869-2fb201f8c569", "name": "Interviewing"}
        ]
    )

    request_body = convert_uuids_to_strings(mock_stages_partial_update.model_dump())

    response = client.patch(
        f"/api/v1/stages?job_id=1",
        json=request_body,
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Stages updated successfully"
    assert response.json()["status"] == 200

@patch("app.models.job.Job.get_by_id", return_value=None)
def test_update_stages_job_not_found(mock_get_by_id):
    # Correcting the data structure to match the expected schema
    mock_stages_partial_update = (StagesPartialUpdate(stages=[
        {"uuid": "fbc5589e-9931-4d60-87ec-0c38bfd9c4e1", "name": "Shortlisted"},
        {"uuid": "7f32cc9e-e5fb-4cfb-9ae7-32e8d13648d1", "name": "Selected"},
        {"uuid": "52795e02-13e4-4452-9322-715001c58ff7", "name": "Rejected"}
    ]))

    response = client.patch(
        f"/api/v1/stages?job_id=1",
        json=convert_uuids_to_strings(mock_stages_partial_update.model_dump()),
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"