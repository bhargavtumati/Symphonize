from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from fastapi.responses import Response
import uuid
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

@patch("app.api.v1.endpoints.jobs.Applicant.get_by_uuid")
@patch("app.helpers.date_helper.convert_epoch_to_utc")
def test_get_applicant(mock_get_applicant, mock_convert_epoch_to_utc):

    applicant_uuid = str(uuid.uuid4()) 
    applicant_update = {"some_key": "some_value"}  # Example update data

    mock_get_applicant.return_value = MagicMock()

    response = client.get(
        f"/api/v1/applicants/{applicant_uuid}",
        headers={"Authorization": "Bearer test_token"}
    )

    print("Response:", response.json())

    assert response.status_code == 200
    assert response.json()["message"] == "Applicant details retrieved successfully"



PERSIMMON_DATA_BUCKET = "PERSIMMON_DATA_BUCKET"  # Ensure the bucket is defined

@patch("app.helpers.gcp_helper.retrieve_from_gcp")
@patch("app.api.v1.endpoints.applicants.Applicant.get_by_uuid")
def test_get_resume(mock_get_applicant, mock_retrieve_from_gcp):
    applicant_uuid = str(uuid.uuid4())

    # ✅ Ensure mock_get_applicant returns an object with a "details" attribute
    applicant_mock = MagicMock()
    applicant_mock.uuid = applicant_uuid
    applicant_mock.details = {
        "original_resume": f"/{PERSIMMON_DATA_BUCKET}/test_resume.pdf",
        "personal_information": {"full_name": "Test User"}
    }

    mock_get_applicant.return_value = applicant_mock  # ✅ Ensure correct return type

    # ✅ Ensure retrieve_from_gcp returns a valid Response
    mock_retrieve_from_gcp.return_value = Response(
        content=b'%PDF-1.4 Test PDF Content',
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="Persimmon_Test_User_Resume.pdf"'}
    )

    # ✅ Make the API request
    response = client.get(
        f"/api/v1/applicants/{applicant_uuid}/resume",
        headers={"Authorization": "Bearer test_token"}
    )

    print("Response headers:", response.headers)
    print("Response content:", response.content[:10])  # Print first 10 bytes for brevity

    # ✅ Assertions
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}, Response: {response.content}"
    assert response.content.startswith(b'%PDF-1.4')
    assert response.headers['Content-Disposition'] == 'attachment; filename="Persimmon_Test_User_Resume.pdf"'






