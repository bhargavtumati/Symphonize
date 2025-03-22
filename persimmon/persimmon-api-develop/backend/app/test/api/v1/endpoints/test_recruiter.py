import pytest
from fastapi.testclient import TestClient
from unittest import mock
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

@mock.patch("app.models.recruiter.Recruiter.get_by_whatsapp_number", return_value=None)
@mock.patch('app.models.recruiter.Recruiter.create', return_value=None)
def test_create_recruiter_success(mock_get_by_whatsapp_number, mock_create):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    payload = {
        "full_name": "sema Smith",
        "whatsapp_number": "6155552671",
        "designation": "Senior Recruiter",
        "linkedin_url": "https://www.linkedin.com/in/janesmith",
        "email_id": "surendra.goluguri@symphonize.com", #change the domain 
        "company": {
            "name": "Nova Innovations Inc.",
            "website": "https://www.techinnovations.com",
            "number_of_employees": "51-200",
            "industry_type": "Staffing and Recruiting",
            "linkedin": "https://www.linkedin.com/company/tech-innovations-inc/",
            "type": "SERVICE_BASED",
            "domain": "sinho.com" #domain need to be changed same as recruiter 
        }
    }
    
    response = client.post("/api/v1/recruiter", json=payload)
    assert response.status_code == 200
    assert response.json()['message'] == "Recruiter created successfully"
    mock_get_by_whatsapp_number.assert_called_once()
    mock_create.assert_called_once()


@mock.patch("app.models.recruiter.Recruiter.get_by_whatsapp_number", return_value=None)
def test_create_recruiter_duplicate_email(mock_get_by_whatsapp_number):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    app.dependency_overrides[Company.get_by_domain] = lambda: {"id": 1}
    app.dependency_overrides[Recruiter.create] = lambda recruiter: (_ for _ in ()).throw(IntegrityError("duplicate key value violates unique constraint", "sql", None))

    payload = {
        "full_name": "sema Smith",
        "whatsapp_number": "6155552671",
        "designation": "Senior Recruiter",
        "linkedin_url": "https://www.linkedin.com/in/janesmith",
        "email_id": "surendra.goluguri@symphonize.com", #change the domain 
        "company": {
            "name": "Nova Innovations Inc.",
            "website": "https://www.techinnovations.com",
            "number_of_employees": "51-200",
            "industry_type": "Staffing and Recruiting",
            "linkedin": "https://www.linkedin.com/company/tech-innovations-inc/",
            "type": "SERVICE_BASED",
            "domain": "sinho.com" 
        }
    }
    
    response = client.post("/api/v1/recruiter", json=payload)
    print("response",response.json())
    assert response.status_code == 409
    assert response.json()['detail'] == "Email already exists, please provide a new Email ID"
    mock_get_by_whatsapp_number.assert_called_once()


@mock.patch("app.models.recruiter.Recruiter.get_by_whatsapp_number", return_value=None)
@mock.patch('app.models.company.Company.get_by_domain', return_value=mock.MagicMock(id=10))
@mock.patch('app.models.recruiter.Recruiter.create', return_value=None)
def test_create_recruiter_with_existing_company(
    mock_get_by_whatsapp_number, 
    mock_get_by_domain, 
    mock_create_recruiter
):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    
    payload = {
        "full_name": "Alice Johnson",
        "whatsapp_number": "8155552673",
        "designation": "Lead Recruiter",
        "linkedin_url": "https://www.linkedin.com/in/alicejohnson",
        "email_id": "surendra.goluguri@symphonize.com",  #change the username in email_id
        "company": {
            "name": "Existing Company",
            "website": "https://www.existingcompany.com",
            "number_of_employees": "201-500",
            "industry_type": "Software Development",
            "linkedin": "https://www.linkedin.com/company/existing-company/",
            "type": "SERVICE_BASED",
            "domain": "symphonize.com"
        }
    }
    
    response = client.post("/api/v1/recruiter", json=payload)
    print("test recruiter response", response.json())
    assert response.status_code == 200
    assert response.json()['message'] == "Recruiter created successfully"
    mock_get_by_whatsapp_number.assert_called_once()
    mock_get_by_domain.assert_called_once()
    mock_create_recruiter.assert_called_once()

# Cleanup the dependency overrides
@pytest.fixture(autouse=True)
def reset_dependencies():
    yield
    app.dependency_overrides = {}


# Test cases for '/update'(update_recruiter) endpoint
def update_recruiter_valid_payload():
    return {
        "full_name": "Kane william",
        "whatsapp_number": "9876543216",
        "designation": "Python Developer",
        "linkedin_url": "https://linkedin.com/in/kane/"
    }

@mock.patch("app.models.recruiter.Recruiter.get_by_whatsapp_number", return_value = None)
@mock.patch("app.models.recruiter.Recruiter.get_by_email_id")
@mock.patch("app.models.recruiter.Recruiter.update_details", return_value=None)
def test_update_recruiter_success(
    mock_update_details,
    mock_recruiter,
    mock_get_by_whatsapp_number
):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    recruiter = mock.MagicMock(full_name="ABC", whatsapp_number="9876543216")
    recruiter.update = mock.MagicMock(return_value=recruiter)
    mock_recruiter.return_value = recruiter

    payload = update_recruiter_valid_payload()

    response = client.patch(url="/api/v1/recruiter/update", json=payload)
    response_payload = response.json()
    assert response.status_code == 200
    assert response_payload['message'] == 'Recruiter details updated successfully'
    assert mock_recruiter.update.call_count == 0
    assert mock_get_by_whatsapp_number.call_count == 0
    mock_recruiter.assert_called_once()
    mock_update_details.assert_called_once()


@mock.patch("app.models.recruiter.Recruiter.get_by_whatsapp_number")
@mock.patch("app.models.recruiter.Recruiter.get_by_email_id")
def test_update_recruiter_with_already_available_whatsapp_number(
    mock_recruiter,
    mock_get_by_whatsapp_number
):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    recruiter = mock.MagicMock(full_name="ABC", whatsapp_number="9876543214")
    recruiter.update = mock.MagicMock(return_value=recruiter)
    mock_recruiter.return_value = recruiter
    mock_get_by_whatsapp_number.return_value = mock.MagicMock(whatsapp_number="9876543218")

    payload = update_recruiter_valid_payload()

    response = client.patch(url="/api/v1/recruiter/update", json=payload)
    
    assert response.status_code == 400
    assert response.json()['detail'] == 'WhatsApp number already exists.'
    assert mock_recruiter.update.call_count == 0
    assert mock_get_by_whatsapp_number.call_count == 1
    mock_recruiter.assert_called_once()
    

@mock.patch("app.models.recruiter.Recruiter.get_by_whatsapp_number", return_value = None)
@mock.patch("app.models.recruiter.Recruiter.get_by_email_id")
@mock.patch("app.models.recruiter.Recruiter.update_details")
def test_update_recruiter_database_error(
    mock_update_details,
    mock_recruiter,
    mock_get_by_whatsapp_number,
):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    recruiter = mock.MagicMock(full_name="ABC", whatsapp_number="9876543216")
    mock_recruiter.return_value = recruiter
    mock_update_details.side_effect = Exception("Database Exception")

    payload = update_recruiter_valid_payload()

    response = client.patch(url="/api/v1/recruiter/update", json=payload)
    response_payload = response.json()
    print("response", response_payload)
    assert response.status_code == 500
    assert "Database Exception" in response_payload['detail'] 
    assert mock_get_by_whatsapp_number.call_count == 0
    mock_recruiter.assert_called_once()
    mock_update_details.assert_called_once()


# Test cases for '/profile/image' (update_recruiter_profile_image) endpoint
@mock.patch("app.models.recruiter.Recruiter.update_profile_image")
@mock.patch("app.models.recruiter.Recruiter.exists_by_email_id", return_value=True)
@mock.patch("app.helpers.gcp_helper.save_image_to_destination", return_value=None)
def test_update_profile_valid_image_upload(mock_save_image_to_destination, mock_exists, mock_update, ):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_update.return_value.rowcount = 1 
    response = client.post(
        url = "/api/v1/recruiter/profile/image",
        files = {"file": ("test.jpg", b"0101010101101", "image/jpeg")},
    )
    assert response.status_code == 200
    print("response payload", response.json())
    assert response.json()['message'] == "Image uploaded successfully"
    mock_update.assert_called_once()
    mock_save_image_to_destination.assert_called_once()
    mock_exists.assert_called_once()

@mock.patch("app.models.recruiter.Recruiter.update_profile_image", return_value=None)
def test_update_profile_invalid_image_type(mock_update):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post(
        url = "/api/v1/recruiter/profile/image",
        files = {"file": ("test.pdf", "These is a pdf", "application/pdf")},
    )
    assert response.status_code == 400
    print("response", response.json())
    assert response.json()["detail"] == "Only JPEG and PNG images are allowed"
    assert mock_update.call_count == 0


def test_update_profile_oversized_image():
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post(
        url = "/api/v1/recruiter/profile/image",
        files={"file": ("large.jpg", b"abc" * (2 * 1024 * 1024 + 1), "image/jpeg")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "File size exceeds 2MB"


@mock.patch("app.models.recruiter.Recruiter.exists_by_email_id")
def test_update_profile_recruiter_not_found(mock_exists):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_exists.return_value = False 
    response = client.post(
        url = "api/v1/recruiter/profile/image",
        files = {"file": ("test.jpg", b"valid_image_data", "image/jpeg")},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "recruiter not found"
    mock_exists.assert_called_once()

@mock.patch("app.models.recruiter.Recruiter.exists_by_email_id")
def test_update_profile_database_error(mock_exists):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_exists.side_effect = Exception("Database error")
    response = client.post(
        "/api/v1/recruiter/profile/image",
        files={"file": ("test.jpg", b"valid_image_data", "image/jpeg")},
    )
    print("response payload", response.json())
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]
    mock_exists.assert_called_once()


# Test cases for '/profile/image' (get_recruiter_profile_image) endpoint
@mock.patch("app.models.recruiter.Recruiter.get_by_email_id")
@mock.patch("app.helpers.gcp_helper.generate_signed_url", return_value=None)
def test_get_recruiter_profile_image_success(mock_generate_signed_url, mock_recruiter):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_recruiter.return_value = mock.MagicMock(profile_image="/persimmon/images/abc.jpg", full_name="John Wick")
    response = client.get("api/v1/recruiter/profile/image")
    assert response.status_code == 200
    response_payload = response.json()
    assert response_payload['message'] == "Recruiter profile image retrived successfully"
    mock_recruiter.assert_called_once()
    mock_generate_signed_url.assert_called_once()


@mock.patch("app.models.recruiter.Recruiter.get_by_email_id", return_value=None)
def test_get_recruiter_profile_image_recruiter_not_found(mock_recruiter):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.get("api/v1/recruiter/profile/image")
    assert response.status_code == 404
    assert response.json()["detail"] == "Recuriter not found."
    mock_recruiter.assert_called_once()


@mock.patch("app.models.recruiter.Recruiter.get_by_email_id", return_value=None)
def test_get_recruiter_profile_image_not_found(mock_recruiter):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_recruiter.return_value = mock.MagicMock(profile_image=None, full_name="John Wick")
    response = client.get("api/v1/recruiter/profile/image")
    assert response.status_code == 200
    response_payload = response.json()
    assert response_payload['profile_image'] == None
    assert response_payload['alternative_text'] == 'JW'
    mock_recruiter.assert_called_once()


@mock.patch("app.models.recruiter.Recruiter.get_by_email_id")
def test_get_recruiter_profile_image_database_error(mock_recruiter):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    mock_recruiter.side_effect = Exception("Database error")  
    response = client.get("api/v1/recruiter/profile/image")
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]
    mock_recruiter.assert_called_once()

