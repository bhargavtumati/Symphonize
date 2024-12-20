import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.models.job import JobTypeEnum, WorkplaceTypeEnum, JobStatusTypeEnum
from app.helpers.firebase_helper import verify_firebase_token

client = TestClient(app)

mock_job_data = {
    "id": 1,
    "title": "Software Engineer",
    "type": JobTypeEnum.FULL_TIME.value,
    "status": JobStatusTypeEnum.ACTIVE.value,
    "workplace_type": WorkplaceTypeEnum.REMOTE.value,
    "location": "Hyderabad",
    "team_size": '6-10',
    "min_salary": 7,
    "max_salary": 12,
    "min_experience": 2,
    "max_experience": 5,
    "target_date": "2024-10-24T10:07:31.962Z",
    "description": "We need 2 to 5 years of experience candidates and the candidate must be proficient in both frontend and with backend",
    "is_posted_for_client": True,
    "company": {
        "id": 1,
        "name": "Symphonize",
        "website": "https://www.symphonize.com",
        "number_of_employees": "51-200",
        "industry_type": "Banking",
        "linkedin": "https://www.linkedin.com/company/symphonize",
        "domain": "symphonize.com",
        "type": "PRODUCT_BASED",
        "meta": {
            "audit": {
                "created_at": "",
                "created_by": {
                    "email": ""
                },
                "updated_at": "",
                "updated_by": {
                    "email": ""
                }
            }
        }
    },
    "ai_clarifying_questions": [{"question": "Are you proficient in Python?","answer": "Yes"}],
    "publish_on_career_page": True,
    "publish_on_job_boards": ["LinkedIn", "Indeed"],
    "meta": {
        "audit": {
            "created_at": "",
            "created_by": {
                "email": ""
            },
            "updated_at": "",
            "updated_by": {
                "email": ""
            }
        }
    }
}

mock_get_job_data = {
    "id": 1,
    "title": "Software Engineer",
    "type": JobTypeEnum.FULL_TIME.value,
    "status": JobStatusTypeEnum.ACTIVE.value,
    "workplace_type": WorkplaceTypeEnum.REMOTE.value,
    "location": "Hyderabad",
    "team_size": '6-10',
    "min_salary": 7,
    "max_salary": 12,
    "min_experience": 2,
    "max_experience": 5,
    "target_date": "2024-10-24T10:07:31.962Z",
    "description": "We need 2 to 5 years of experience candidates and the candidate must be proficient in both frontend and with backend",
    "is_posted_for_client": True,
    "company_id": 1,
    "ai_clarifying_questions": [{"question": "Are you proficient in Python?","answer": "Yes"}],
    "publish_on_career_page": True,
    "publish_on_job_boards": ["LinkedIn", "Indeed"],
    "meta": {
        "audit": {
            "created_at": "",
            "created_by": {
                "email": ""
            },
            "updated_at": "",
            "updated_by": {
                "email": ""
            }
        }
    }
}

mock_job_update_data = {
    "title": "Senior Software Engineer",
    "type": JobTypeEnum.FULL_TIME.value,
    "status": JobStatusTypeEnum.ACTIVE.value,
    "workplace_type": WorkplaceTypeEnum.REMOTE.value,
    "location": "Hyderabad",
    "team_size": '6-10',
    "min_salary": 7,
    "max_salary": 12,
    "min_experience": 2,
    "max_experience": 5,
    "target_date": "2024-10-24T10:07:31.962Z",
    "description": "We need 2 to 5 years of experience candidates and the candidate must be proficient in both frontend and with backend",
    "is_posted_for_client": True,
    "company": {
        "name": "Symphonize",
        "website": "https://www.symphonize.com",
        "number_of_employees": "201-500",
        "industry_type": "Banking",
        "linkedin": "https://www.linkedin.com/company/symphonize",
        "domain": "symphonize.com",
        "type": "PRODUCT_BASED",
        "meta": {
            "audit": {
                "created_at": "",
                "created_by": {
                    "email": ""
                },
                "updated_at": "",
                "updated_by": {
                    "email": ""
                }
            }
        }
    },
    "ai_clarifying_questions": [{"question": "Are you proficient in Python?","answer": "Yes"}],
    "publish_on_career_page": True,
    "publish_on_job_boards": ["LinkedIn", "Indeed"],
    "meta": {
        "audit": {
            "created_at": "",
            "created_by": {
                "email": ""
            },
            "updated_at": "",
            "updated_by": {
                "email": ""
            }
        }
    }
}

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"
    }

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

@patch("app.models.company.Company.get_by_domain")
@patch("app.models.company.Company.create")
@patch("app.models.job.Job.create")
def test_create_job_posting_success(mock_create_job, mock_create_company, mock_get_company_by_domain):
    # Mock the database calls
    mock_get_company_by_domain.return_value = None
    mock_create_company.return_value = MagicMock(id=1)
    mock_create_job.return_value = mock_get_job_data

    response = client.post("/api/v1/jobs", json=mock_job_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Job created successfully"
    assert response.json()["data"]["title"] == "Software Engineer"

    #assert mock api calls
    assert mock_create_company.call_count == 1 
    assert mock_create_job.call_count == 1

@patch("app.models.company.Company.get_by_domain")
@patch("app.models.company.Company.create")
@patch("app.models.job.Job.create")
def test_create_job_posting_existing_company(mock_create_job, mock_create_company, mock_get_company_by_domain):
    # Mock the database calls
    mock_get_company_by_domain.return_value = MagicMock(id=1)
    mock_create_job.return_value = mock_get_job_data

    response = client.post("/api/v1/jobs", json=mock_job_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Job created successfully"

    #assert mock api calls
    assert mock_create_company.call_count == 0 
    assert mock_create_job.call_count == 1

@patch("app.models.job.Job.get_count")
@patch("app.models.job.Job.get_all")
@patch("app.models.company.Company.get_by_id")
def test_get_jobs(mock_get_company_by_id, mock_get_jobs, mock_get_total_jobs_count):
    # Mock the database calls
    mock_get_total_jobs_count.return_value = 2
    mock_get_jobs.return_value = [
        MagicMock(id=1, title='Angular Developer', location='Hyderabad', status='ACTIVE', meta={'audit':{'created_at':1727946266.0931342}}),
        MagicMock(id=2, title='Next JS Developer', location='Hyderabad', status='ACTIVE', meta={'audit':{'created_at':1727946661.1225376}}, is_posted_for_client=True)
    ]  
    mock_get_company_by_id.return_value = MagicMock(name='symphonize')

    response = client.get("/api/v1/jobs/?page=1")
    assert response.status_code == 200
    assert response.json()['jobs'][0]['title'] == 'Angular Developer'
    assert response.json()['pagination']['total_pages'] == 1

    #assert mock api calls
    assert mock_get_total_jobs_count.call_count == 1
    assert mock_get_jobs.call_count == 1

@patch("app.models.job.Job.update")
@patch("app.models.job.Job.get_by_id")
def test_partial_update_job(mock_get_job_by_id, mock_partial_update_job):
    mock_get_job_by_id.return_value = MagicMock(id=1, status="ACTIVE")
    mock_partial_update_job.return_value = MagicMock(id=1, status="CLOSED")

    partial_update_data = {
        "status": "CLOSED"
    }

    response = client.patch("/api/v1/jobs/1", json=partial_update_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Job status updated successfully"

@patch("app.models.company.Company.update")
@patch("app.models.company.Company.get_by_id")
@patch("app.models.job.Job.update")
@patch("app.models.job.Job.get_by_id")
def test_update_job(mock_get_job_by_id, mock_update_job, mock_get_company_by_id, mock_update_company):
    job_data = MagicMock()
    job_data.meta = {'audit': {'updated_by': {'email':'surendra21@xyz.com'}}}
    mock_get_job_by_id.return_value = job_data
    mock_update_job.return_value = mock_job_update_data

    company_data = MagicMock()
    company_data.meta = {'audit': {'updated_by': {'email':'surendra21@xyz.com'}}}
    mock_get_company_by_id.return_value = company_data
    mock_update_company.return_value = mock_job_update_data["company"]

    response = client.put("/api/v1/jobs/1", json=mock_job_update_data)
    assert response.status_code == 200

@patch("app.models.job.Job.get_by_id")
@patch("app.models.company.Company.get_by_id")
def test_get_job_by_id(mock_get_company_by_id, mock_get_job_by_id):
    mock_get_job_by_id.return_value = MagicMock(id=1, title="Software Engineer", location="Hyderabad", status="ACTIVE", company_id=1)
    mock_get_company_by_id.return_value = MagicMock(id=1, name="symphonize")

    response = client.get("/api/v1/jobs/1")
    assert response.status_code == 200
    assert mock_get_job_by_id.call_count == 1
