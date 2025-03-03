import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.models.recruiter import Recruiter
from app.models.company import Company
from app.models.template import Template
from app.helpers.firebase_helper import verify_firebase_token
from fastapi.responses import JSONResponse


client = TestClient(app)

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"
    }

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

mock_recruiter_data = {
        "full_name": "Surendra Goluguri",
        "whatsapp_number": "6155552671",
        "designation": "Senior Recruiter",
        "linkedin_url": "https://www.linkedin.com/in/surendragoluguri",
        "email_id": "surendra.goluguri@symphonize.com", #change the domain 
        "company": {
            "name": "Symphonize Inc.",
            "website": "https://www.symphonize.com",
            "number_of_employees": "51-200",
            "industry_type": "Staffing and Recruiting",
            "linkedin": "https://www.linkedin.com/company/Symphonizeinc/",
            "type": "SERVICE_BASED",
            "domain": "symphonize.com" #domain need to be changed same as recruiter 
        }
}

mock_created_recruiter = {
    "id":1,
    "full_name": "Surendra Goluguri",
        "whatsapp_number": "6155552671",
        "designation": "Senior Recruiter",
        "linkedin_url": "https://www.linkedin.com/in/surendragoluguri",
        "email_id": "surendra.goluguri@symphonize.com", #change the domain 
        "company": {
            "name": "Symphonize Inc.",
            "website": "https://www.symphonize.com",
            "number_of_employees": "51-200",
            "industry_type": "Staffing and Recruiting",
            "linkedin": "https://www.linkedin.com/company/Symphonizeinc/",
            "type": "SERVICE_BASED",
            "domain": "symphonize.com" #domain need to be changed same as recruiter 
        },
        "company_id": 1
}


@patch("app.models.recruiter.Recruiter.get_by_whatsapp_number")
@patch("app.models.company.Company.get_by_domain")
@patch("app.models.company.Company.create")
@patch("app.models.template.Template.create")
@patch("app.models.recruiter.Recruiter.create")
@patch("app.models.master_data.MasterData.validate_value_by_type")
def test_create_recruiter(mock_validate_value_by_type,mock_create_recruiter, mock_create_template, mock_create_company, mock_get_company_by_domain, mock_get_by_whatsapp_number):
    # Mock the database calls
    mock_get_by_whatsapp_number.return_value = None
    mock_get_company_by_domain.return_value = None
    mock_validate_value_by_type.return_value = True
    mock_create_company.return_value = MagicMock(id=1)
    mock_create_recruiter.return_value = mock_created_recruiter

    response = client.post("/api/v1/recruiter", json=mock_recruiter_data)

    print("Response JSON:", response.json())

    assert response.status_code == 201
    assert response.json()["message"] == "Recruiter created successfully"

@patch("app.models.recruiter.Recruiter.exists_by_email_id")
def test_verify_recruiter_by_email(mock_exists_by_email_id):
   
    # Mock the database call
    mock_exists_by_email_id.return_value = True

    response = client.get("/api/v1/recruiter/john.doe@test.com")

    print("Response JSON:", response.json())
    assert response.status_code == 200
    assert response.json() is True

@patch("app.models.recruiter.Recruiter.get_by_created_by_email")
def test_get_recruiter(mock_get_by_created_by_email):
    # Mock the database call
    mock_get_by_created_by_email.return_value = MagicMock(
        full_name="John Doe",
        whatsapp_number="1234567890",
        designation="HR Manager",
        linkedin_url="https://www.linkedin.com/in/johndoe",
        email_id="john.doe@test.com"
    )

    response = client.get("/api/v1/recruiter")

    print("Response JSON:", response.json())

    assert response.status_code == 200
    assert response.json()["message"] == "Recruiter fetched successfully"
    assert response.json()["recuriter"]["full_name"] == "John Doe"
    assert response.json()["recuriter"]["whatsapp_number"] == "1234567890"
    assert response.json()["recuriter"]["designation"] == "HR Manager"
    assert response.json()["recuriter"]["linkedin_url"] == "https://www.linkedin.com/in/johndoe"
    assert response.json()["recuriter"]["email_id"] == "john.doe@test.com"
