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
    "description": "<p><strong>Senior Java Developer</strong></p>\n<p><strong>Responsibilities:</strong></p>\n<ul>\n<li>Lead and mentor junior developers</li>\n<li>Design, develop, and implement complex software solutions using Java</li>\n<li>Optimize application performance and scalability</li>\n</ul>\n<p><strong>Qualifications:</strong></p>\n<ul>\n<li>5+ years of experience in Java development</li>\n<li>Strong understanding of object-oriented programming concepts</li>\n<li>Expertise in enterprise Java frameworks such as Spring, Hibernate, and JPA</li>\n</ul>\n<p><strong>Additional Desired Skills:</strong></p>\n<ul>\n<li>Experience with big data technologies (e.g., Hadoop, Spark)</li>\n<li>Knowledge of agile development methodologies</li>\n<li>Certification in Java or related technologies</li>\n</ul>\n<p><strong>Responsibilities and Expectations</strong></p>\n<ul>\n<li><strong>Lead and mentor junior developers:</strong> Provide guidance and support to team members, fostering their growth and development.</li>\n<li><strong>Design, develop, and implement complex software solutions:</strong> Translate business requirements into technical specifications and develop robust, scalable applications.</li>\n<li><strong>Optimize application performance and scalability:</strong> Identify bottlenecks and implement solutions to improve application performance and efficiency.</li>\n</ul>\n<p><strong>Qualifications</strong></p>\n<ul>\n<li><strong>5+ years of experience in Java development:</strong> Demonstrated proficiency in core Java concepts and enterprise Java frameworks.</li>\n<li><strong>Strong understanding of object-oriented programming concepts:</strong> Ability to design and implement complex software systems using OOP principles.</li>\n<li><strong>Excellent communication and interpersonal skills:</strong> Ability to communicate complex technical concepts effectively and work collaboratively with a diverse team.</li>\n</ul>" * 3,
    "is_posted_for_client": True,
    "company": {
        "id": 1,
        "name": "Symphonize",
        "website": "https://www.symphonize.com",
        "number_of_employees": "51-200",
        "industry_type": "Banking",
        "linkedin": "https://www.linkedin.com/company/symphonize/",
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
    "enhanced_description": {},
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
    "description": "<p><strong>Senior Java Developer</strong></p>\n<p><strong>Responsibilities:</strong></p>\n<ul>\n<li>Lead and mentor junior developers</li>\n<li>Design, develop, and implement complex software solutions using Java</li>\n<li>Optimize application performance and scalability</li>\n</ul>\n<p><strong>Qualifications:</strong></p>\n<ul>\n<li>5+ years of experience in Java development</li>\n<li>Strong understanding of object-oriented programming concepts</li>\n<li>Expertise in enterprise Java frameworks such as Spring, Hibernate, and JPA</li>\n</ul>\n<p><strong>Additional Desired Skills:</strong></p>\n<ul>\n<li>Experience with big data technologies (e.g., Hadoop, Spark)</li>\n<li>Knowledge of agile development methodologies</li>\n<li>Certification in Java or related technologies</li>\n</ul>\n<p><strong>Responsibilities and Expectations</strong></p>\n<ul>\n<li><strong>Lead and mentor junior developers:</strong> Provide guidance and support to team members, fostering their growth and development.</li>\n<li><strong>Design, develop, and implement complex software solutions:</strong> Translate business requirements into technical specifications and develop robust, scalable applications.</li>\n<li><strong>Optimize application performance and scalability:</strong> Identify bottlenecks and implement solutions to improve application performance and efficiency.</li>\n</ul>\n<p><strong>Qualifications</strong></p>\n<ul>\n<li><strong>5+ years of experience in Java development:</strong> Demonstrated proficiency in core Java concepts and enterprise Java frameworks.</li>\n<li><strong>Strong understanding of object-oriented programming concepts:</strong> Ability to design and implement complex software systems using OOP principles.</li>\n<li><strong>Excellent communication and interpersonal skills:</strong> Ability to communicate complex technical concepts effectively and work collaboratively with a diverse team.</li>\n</ul>"*3,
    "is_posted_for_client": True,
    "company": {
        "name": "Symphonize",
        "website": "https://www.symphonize.com",
        "number_of_employees": "201-500",
        "industry_type": "Banking",
        "linkedin": "https://www.linkedin.com/company/symphonize/",
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
    "enhanced_description": {},
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

@patch("app.helpers.company_helper.get_or_create_company")
@patch("app.models.recruiter.Recruiter.get_by_email_id")
@patch("app.models.company.Company.get_by_id")
@patch("app.helpers.job_helper.generate_job_code")
@patch("app.helpers.jd_helper.extract_features_from_jd")
@patch("app.helpers.job_helper.enhance_jd")
@patch("app.models.job.Job.create")
@patch("app.helpers.stages_helper.create_stages")
def test_create_job_success(
    mock_create_stages,
    mock_create_job,
    mock_enhance_jd,
    mock_extract_features,
    mock_generate_code,
    mock_get_company,
    mock_get_recruiter,
    mock_get_or_create_company,
):
    mock_recruiter = MagicMock(id=1, company_id=2)
    mock_get_recruiter.return_value = mock_recruiter
    
    mock_company = MagicMock(id=2, name="TestCorp")
    mock_get_company.return_value = mock_company
    mock_generate_code.return_value = "Sym0001"
    
    mock_extract_features.return_value = {}
    mock_enhance_jd.return_value = {}

    mock_job = MagicMock(id=10, code="Sym0001")
    mock_create_job.return_value = mock_job
    mock_get_or_create_company.return_value = mock_company
    
    mock_create_stages.return_value = None
    
    # API call
    response = client.post("/api/v1/jobs", json=mock_job_data)
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["message"] == "Job created successfully"
    assert response.json()["data"]["id"] == 10
    assert response.json()["data"]["code"] == "Sym0001"
    
    # Verify mocks were called
    mock_get_recruiter.assert_called_once()
    mock_extract_features.assert_called_once()
    mock_create_job.assert_called_once()

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

@patch("app.models.job.Job.get_by_id")
@patch("app.helpers.job_helper.prepare_job_data")
@patch("app.helpers.db_helper.update_meta")
@patch("app.helpers.company_helper.handle_company_association")
@patch("app.models.job.Job.update")
def test_update_job_success(
    mock_update_job,
    mock_handle_company,
    mock_update_meta,
    mock_prepare_job_data,
    mock_get_job
):
    mock_job = MagicMock(id=1, title="Software Engineer", meta={})
    mock_get_job.return_value = mock_job
    
    mock_prepare_job_data.return_value = {"title": "Senior Software Engineer"}
    mock_update_meta.return_value = {"updated_by": "test@example.com"}
    
    mock_handle_company.return_value = {"company_id": 2, "name": "TestCorp"}
    
    mock_updated_job = MagicMock(id=1, title="Senior Software Engineer")
    mock_update_job.return_value = mock_updated_job
    
    # API call
    response = client.put("/api/v1/jobs/1", json=mock_job_update_data)
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["message"] == "Job updated successfully"
    
    mock_get_job.assert_called_once()

@patch("app.models.job.Job.get_by_id")
@patch("app.models.company.Company.get_by_id")
def test_get_job_by_id(mock_get_company_by_id, mock_get_job_by_id):
    mock_get_job_by_id.return_value = MagicMock(id=1, title="Software Engineer", location="Hyderabad", status="ACTIVE", company_id=1)
    mock_get_company_by_id.return_value = MagicMock(id=1, name="symphonize")

    response = client.get("/api/v1/jobs/1")
    assert response.status_code == 200
    assert mock_get_job_by_id.call_count == 1
