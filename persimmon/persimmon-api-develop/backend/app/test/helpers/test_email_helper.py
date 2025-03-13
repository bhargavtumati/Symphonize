import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.helpers.email_helper import render_email_variables
from app.models.applicant import Applicant
from app.models.company import Company
from app.models.job import Job
from app.models.recruiter import Recruiter
from fastapi import HTTPException

@patch("app.models.applicant.Applicant.get_by_emailid_and_job_id")
def test_render_email_variables(mock_get_applicant):
    mock_session = MagicMock(spec=Session)

    mock_applicant = MagicMock()
    mock_applicant.details = {
        "personal_information": {"full_name": "Charan reddy"}
    }
    mock_get_applicant.return_value = mock_applicant  # Simulating a found applicant

    mock_company = MagicMock(spec=Company)
    mock_company.name = "Tekworks"
    mock_company.industry_type = "Software"
    mock_company.type.name = "Private"
    mock_company.number_of_employees = 500
    mock_company.website = "https://tekworks.in"

    mock_job = MagicMock(spec=Job)
    mock_job.id = 1
    mock_job.title = "Software Engineer"
    mock_job.type.name = "Full-Time"
    mock_job.workplace_type.name = "Remote"
    mock_job.location = "Hyderabad"
    mock_job.min_experience = 3
    mock_job.max_experience = 5
    mock_job.min_salary = 60000
    mock_job.max_salary = 90000

    mock_recruiter = MagicMock(spec=Recruiter)
    mock_recruiter.full_name = "Surendra"
    mock_recruiter.designation = "HR Manager"
    mock_recruiter.whatsapp_number = "1234567890"

    to_email = "candidate@example.com"
    body_template = "Hello {{ CandidateName }}, your job application for {{ JobTitle }} at {{ CompanyName }} has been received."
    subject_template = "{{ JobTitle }} Interview Invitation at {{ CompanyName }}"

    body, subject = render_email_variables(
        session=mock_session,
        to_email=to_email,
        body=body_template,
        subject=subject_template,
        company=mock_company,
        job=mock_job,
        recuriter=mock_recruiter
    )

    assert "Hello Charan reddy" in body
    assert "Software Engineer" in body
    assert "Tekworks" in body
    assert "Software Engineer Interview Invitation at Tekworks" in subject

    mock_get_applicant.assert_called_once_with(session=mock_session, emailid=to_email, job_id=1)


def test_render_email_variables_applicant_not_found():
    """Test when applicant is not found"""
    with patch("app.models.applicant.Applicant.get_by_emailid_and_job_id", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            render_email_variables(
                session=MagicMock(),
                to_email="candidate@example.com",
                body="Hello {{ CandidateName }}",
                subject="{{ JobTitle }}",
                company=MagicMock(),
                job=MagicMock(id=1),
                recuriter=MagicMock()
            )

    assert exc_info.value.status_code == 404
    assert "Applicant not found" in str(exc_info.value.detail)
