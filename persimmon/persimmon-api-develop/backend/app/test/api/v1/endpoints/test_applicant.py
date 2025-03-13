from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.helpers.firebase_helper import verify_firebase_token

client = TestClient(app)

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"
    }

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token


@patch("app.api.v1.endpoints.jobs.Job.get_by_id")
@patch("app.api.v1.endpoints.jobs.Stages.get_by_id")
@patch("app.api.v1.endpoints.jobs.Applicant.get_by_uuid")
@patch("app.api.v1.endpoints.jobs.solrh.update_solr_documents_partially")
def test_partial_update_success(
    mock_solr_update,
    mock_get_applicant,
    mock_get_stages,
    mock_get_job,
):
    # Mock job retrieval
    mock_get_job.return_value = MagicMock()
    
    # Mock stages retrieval
    mock_get_stages.return_value = MagicMock(
        stages=[
            {"uuid": "52795e02-13e4-4452-9322-715001c58ff7", "name": "interview"},
            {"uuid": "7f32cc9e-e5fb-4cfb-9ae7-32e8d13648d1", "name": "hired"}
        ]
    )
    
    # Mock applicant retrieval
    mock_applicant = MagicMock()
    mock_get_applicant.return_value = mock_applicant
    
    # Mock Solr update success
    mock_solr_update.return_value = None
    
    payload = {
        "applicant_uuids": ["fbc5589e-9931-4d60-87ec-0c38bfd9c4e1"],
        "stage_uuid": "7f32cc9e-e5fb-4cfb-9ae7-32e8d13648d1"
    }
    
    response = client.patch("/api/v1/applicants?job_id=1", json=payload)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully moved to hired"

@patch("app.api.v1.endpoints.jobs.Job.get_by_id", return_value=None)
def test_partial_update_job_not_found(mock_get_job):
    payload = {
        "applicant_uuids": ["fbc5589e-9931-4d60-87ec-0c38bfd9c4e1"],
        "stage_uuid": "7f32cc9e-e5fb-4cfb-9ae7-32e8d13648d1"
    }
    
    response = client.patch("/api/v1/applicants?job_id=1", json=payload)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

@patch("app.api.v1.endpoints.jobs.Stages.get_by_id")   #give the method to MajicMock- 
@patch("app.api.v1.endpoints.jobs.Job.get_by_id")      
@patch("app.api.v1.endpoints.jobs.Applicant.get_by_uuid")
@patch("app.api.v1.endpoints.jobs.solrh.update_solr_documents_partially")
def test_partial_update_invalid_stage( mock_solr_update,
    mock_get_applicant,
    mock_get_stages,            
    mock_get_job):   #majic mock will give mock stages, applicants and they are passed to the test method
    payload = {
        "applicant_uuids": ["fbc5589e-9931-4d60-87ec-0c38bfd9c4e1"],
        "stage_uuid": "ee6ec4f0-b47c-4748-92c6-97ace111a725"
    }
    
    response = client.patch("/api/v1/applicants?job_id=1", json=payload)    #call the endpoint by giving necessary params
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid stage uuid"    #test is passed if expected result is same like what is expected

@pytest.fixture
def mock_applicant():
    mock = MagicMock()
    mock.feedback = [
        {
        "rating": {"skill": 3, "communication": 3, "professionalism": 3},
        "overall_feedback": "string",
        "opinion": "dislike",
        "given_by": "user1@example.com"
         }
    ]
    return mock


@patch("app.api.v1.endpoints.applicants.Applicant.get_by_uuid", return_value=None)
def test_add_feedback_applicant_not_found(mock_get_applicant):
    response = client.post("/api/v1/applicants/fbc5589e-9931-4d60-87ec-0c38bfd9c4e1/feedback", json={"feedback": []})
    assert response.status_code == 404
    assert response.json()["detail"] == "Applicant not found"

@patch("app.api.v1.endpoints.applicants.Applicant.get_by_uuid")
def test_add_feedback_invalid_feedback_format(mock_get_applicant, mock_applicant):
    mock_get_applicant.return_value = mock_applicant

    response = client.post("/api/v1/applicants/fbc5589e-9931-4d60-87ec-0c38bfd9c4e1/feedback", json={"feedback": {}})
    assert response.status_code == 422

@patch("app.api.v1.endpoints.applicants.Applicant.get_by_uuid")
def test_add_feedback_success(mock_get_applicant, mock_applicant):
    mock_get_applicant.return_value = mock_applicant

    payload = [{
            "rating": {"skill": 5, "communication": 4, "professionalism": 4},
            "overall_feedback": "Great work",
            "opinion": "like",
            "given_by": "user@example.com"
        }]

    response = client.post("/api/v1/applicants/fbc5589e-9931-4d60-87ec-0c38bfd9c4e1/feedback",
                           json={"feedback": payload})

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Feedback updated successfully"

@patch("app.api.v1.endpoints.applicants.Applicant.get_by_uuid")
def test_add_feedback_db_error(mock_get_applicant, mock_applicant):
    mock_get_applicant.return_value = mock_applicant
    mock_applicant.update.side_effect = Exception("Database error")

    payload = [{
            "rating": {"skill": 5, "communication": 4, "professionalism": 4},
            "overall_feedback": "Great work",
            "opinion": "like",
            "given_by": "user@example.com"
        }]

    response = client.post("/api/v1/applicants/fbc5589e-9931-4d60-87ec-0c38bfd9c4e1/feedback",
                           json={"feedback": payload})

    assert response.status_code == 500
    assert "Unexpected Error" in response.json()["detail"]