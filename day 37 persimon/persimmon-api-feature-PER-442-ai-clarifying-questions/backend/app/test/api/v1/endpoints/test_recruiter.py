import pytest
from fastapi.testclient import TestClient
from app.main import app  # Import your FastAPI app here
from sqlalchemy.exc import IntegrityError
from app.models.company import Company
from app.models.recruiter import Recruiter
from app.helpers.firebase_helper import verify_firebase_token

client = TestClient(app)

# Mock functions to replace actual database calls if necessary
def mock_create_company(company_data):
    return {"id": 1}

def mock_get_company_details_non_existent(domain):
    return None  # Simulating that the company does not exist

def mock_get_company_details_existing(domain):
    return {"id": 1}  # Simulating that the company already exists with this ID

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"
    }

# Dependency overrides
app.dependency_overrides[Company.get_by_domain] = mock_get_company_details_non_existent
app.dependency_overrides[Company.create] = mock_create_company

def test_create_recruiter_success():
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    payload = {
        "full_name": "sema Smith",
        "whatsapp_number": "6155552671",
        "designation": "Senior Recruiter",
        "linkedin_url": "https://www.linkedin.com/in/janesmith",
        "email_id": "gemma@sinho.com", #change the domain 
        "company": {
            "name": "Nova Innovations Inc.",
            "website": "https://www.techinnovations.com",
            "number_of_employees": "51-200",
            "industry_type": "Staffing and Recruiting",
            "linkedin": "https://www.linkedin.com/company/tech-innovations-inc",
            "type": "SERVICE_BASED",
            "domain": "sinho.com" #domain need to be changed same as recruiter 
        }
    }
    
    response = client.post("/api/v1/recruiter", json=payload)
    assert response.status_code == 200
    assert response.json()['message'] == "Recruiter created successfully"

def test_create_recruiter_duplicate_email():
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    app.dependency_overrides[Recruiter.create] = lambda recruiter: (_ for _ in ()).throw(IntegrityError("duplicate key value violates unique constraint", "sql", None))

    payload = {
        "full_name": "Jane Doe",
        "whatsapp_number": "7155552672",
        "designation": "Junior Recruiter",
        "linkedin_url": "https://www.linkedin.com/in/janedoe",
        "email_id": "gemma@sinho.com",  # Same email as before
        "company": {
            "name": "Nova Innovations Inc.",
            "website": "https://www.techinnovations.com",
            "number_of_employees": "51-200",
            "industry_type": "Staffing and Recruiting",
            "linkedin": "https://www.linkedin.com/company/tech-innovations-inc",
            "type": "SERVICE_BASED",
            "domain": "sinho.com"
        }
    }

    response = client.post("/api/v1/recruiter", json=payload)
    assert response.status_code == 409
    assert response.json() == {"detail": "Email already exists, please provide a new Email ID"}

def test_create_recruiter_with_existing_company():
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    app.dependency_overrides[Company.get_by_domain] = mock_get_company_details_existing
    
    payload = {
        "full_name": "Alice Johnson",
        "whatsapp_number": "8155552673",
        "designation": "Lead Recruiter",
        "linkedin_url": "https://www.linkedin.com/in/alicejohnson",
        "email_id": "marry@symphonize.com",  #change the username in email_id
        "company": {
            "name": "Existing Company",
            "website": "https://www.existingcompany.com",
            "number_of_employees": "201-500",
            "industry_type": "Software Development",
            "linkedin": "https://www.linkedin.com/company/existing-company",
            "type": "SERVICE_BASED",
            "domain": "symphonize.com"
        }
    }
    
    response = client.post("/api/v1/recruiter", json=payload)
    
    assert response.status_code == 200
    assert response.json()['message'] == "Recruiter created successfully"

# Cleanup the dependency overrides
@pytest.fixture(autouse=True)
def reset_dependencies():
    yield
    app.dependency_overrides = {}