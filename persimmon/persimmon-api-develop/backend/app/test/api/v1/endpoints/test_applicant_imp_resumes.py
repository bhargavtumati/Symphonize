import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app is named 'app'
from sqlalchemy.orm import Session
from fastapi import status
from app.helpers.firebase_helper import verify_firebase_token
from app.db.session import get_db

client = TestClient(app)

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"
    }

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token



@pytest.fixture
def mock_job():
    job = MagicMock()
    job.id = 1
    job.description = "Test Job Description"
    return job

@pytest.fixture
def resume_file_pdf():
    return ("test_resume.pdf", b"sample content", "application/pdf")

@pytest.fixture
def resume_file_docx():
    return ("test_resume.docx", b"sample content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@pytest.fixture
def resume_file_invalid():
    return ("test_resume.txt", b"sample content", "text/plain")

def override_get_db():
    db = MagicMock(spec=Session)
    yield db

app.dependency_overrides[get_db] = override_get_db

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import UploadFile
from io import BytesIO
from app.main import app  # adjust this import based on your app location

@pytest.mark.asyncio
async def test_upload_resume_200_ok():
    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.description = "Mock Job Description"

    mock_stages = MagicMock()
    mock_stages.stages = [{"uuid": "stage-uuid"}]

    mock_applicant = MagicMock()
    mock_applicant.uuid = "mock-applicant-uuid"

    file_content = b"%PDF-1.4 mock content"


    with patch("app.api.v1.endpoints.applicants.Job.get_by_code", return_value=mock_job), \
         patch("app.api.v1.endpoints.applicants.Stages.get_by_id", return_value=mock_stages), \
         patch("app.api.v1.endpoints.applicants.Applicant.create", return_value=mock_applicant), \
         patch("app.api.v1.endpoints.applicants.pdfh.extract_text_from_file", new_callable=AsyncMock, return_value="Mock resume text"), \
         patch("app.api.v1.endpoints.applicants.Applicant.get_by_mobile_number", new_callable=AsyncMock, return_value=None), \
         patch("app.api.v1.endpoints.applicants.Applicant.get_by_email_id", new_callable=AsyncMock, return_value=None), \
         patch("app.api.v1.endpoints.applicants.ap.resume_process", new_callable=AsyncMock):

        async with AsyncClient(app=app, base_url="http://test") as client:
            response1 = await client.post(
                "api/v1/applicants/upload-resume/?job_code=mock-job-code",
                files=[
                    ("file", ("resume1.pdf", file_content, "application/pdf")),
                    ("files", ("resume2.pdf", file_content, "application/pdf")),
                ],
                headers={"Authorization": "Bearer fake_token"} 
            )
           
    assert response1.status_code == 200

    print("Response 1:", response1.json())


@pytest.mark.asyncio
async def test_upload_resume_invalid_file_format():
    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.description = "Mock Job Description"

    invalid_file_content = b"This is a text file pretending to be a resume."

    with patch("app.api.v1.endpoints.applicants.Job.get_by_code", return_value=mock_job):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/applicants/upload-resume/?job_code=mock-job-code",
                files=[
                    ("files", ("resume1.txt", invalid_file_content, "text/plain")),
                    ("files", ("resume2.csv", invalid_file_content, "text/csv")),
                ],
                headers={"Authorization": "Bearer fake_token"}
            )

    assert response.status_code == 400
    assert response.json()["detail"] == "No valid files found"

    print("Invalid format response:", response.json())



@pytest.mark.asyncio
async def test_upload_resume_duplicate_detected():
    mock_job = MagicMock()
    mock_job.id = 1
    mock_job.description = "Mock Job Description"

    file_content = b"%PDF-1.4 mock content with email test@example.com and phone 1234567890"

    # Mock an applicant already present with same mobile or email
    mock_existing_applicant = MagicMock()
    mock_existing_applicant.uuid = "existing-applicant-uuid"

    with patch("app.api.v1.endpoints.applicants.Job.get_by_code", return_value=mock_job), \
         patch("app.api.v1.endpoints.applicants.pdfh.extract_text_from_file", new_callable=AsyncMock, return_value="test@example.com 1234567890"), \
         patch("app.api.v1.endpoints.applicants.Applicant.get_by_mobile_number", new_callable=AsyncMock, return_value=mock_existing_applicant), \
         patch("app.api.v1.endpoints.applicants.Applicant.get_by_email_id", new_callable=AsyncMock, return_value=None):

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/applicants/upload-resume/?job_code=mock-job-code",
                files=[
                    ("files", ("resume1.pdf", file_content, "application/pdf")),
                ],
                headers={"Authorization": "Bearer fake_token"}
            )

    assert response.status_code == 200

    json_data = response.json()
    assert json_data["status"] == "partial success"
    assert json_data["uploaded_files"] == []
    assert "Duplicate detected: resume1.pdf" in json_data["duplicates"]

    print("Duplicate detection response:", json_data)

