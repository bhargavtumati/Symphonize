import pytest, io, json
from unittest import mock
from fastapi.testclient import TestClient
from app.main import app
from app.helpers.firebase_helper import verify_firebase_token

client = TestClient(app)

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"
    }

def test_update_company_success():
    mock_company = mock.Mock()

    mock_company.configure_mock(**{
        "name": "Old Company",
        "website": "https://www.oldwebsite.com",
        "number_of_employees": "51-200",
        "linkedin": "https://www.linkedin.com/company/old-company/",
        "type": "SERVICE_BASED",
        "meta": {},
        "images": []
    })
    
    with mock.patch("app.models.company.Company.get_by_domain", return_value=mock_company) as mock_get_by_domain, \
         mock.patch("app.models.company.Company.update", return_value=None), \
         mock.patch("app.helpers.db_helper.update_meta", return_value={}):

        app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
        
        payload = {
            "name": "Updated Company Name",
            "website": "https://www.updatedwebsite.com",
            "number_of_employees": "201-500",
            "linkedin": "https://www.linkedin.com/company/updated-company/",
            "type": "SERVICE_BASED"
        }

        response = client.patch("/api/v1/company", data=payload)
        assert response.status_code == 200
        assert response.json()['message'] == "Company details updated successfully"
        mock_get_by_domain.assert_called_once()

def test_update_company_not_found():
    with mock.patch("app.models.company.Company.get_by_domain", return_value=None):
        app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
        
        response = client.patch("/api/v1/company", data={"name": "New Company"})
        assert response.status_code == 404
        assert response.json()['detail'] == "Company not found"

def test_invalid_logo_upload():
    mock_company = mock.Mock()
    with mock.patch("app.models.company.Company.get_by_domain", return_value=mock_company):
        app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
        invalid_file = ("invalid.txt", b"invalid content", "text/plain")
        
        response = client.patch(
            "/api/v1/company",
            files={"logo": invalid_file}
        )
        assert response.status_code == 400
        assert response.json()['detail'] == "Logo must be a PNG or JPEG image."

@mock.patch("app.models.company.Company.get_by_domain")
@mock.patch("app.helpers.gcp_helper.save_image_to_destination")
def test_update_company_images_exceed_limit(mock_save_image_to_destination, mock_get_by_domain):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

    mock_get_by_domain.return_value = mock.Mock(images=["img1.jpg"] * 10)
    mock_save_image_to_destination.return_value = "path/to/image.jpg"
    
    # Simulate 2 additional images
    image_data = io.BytesIO(b"testimage")
    files = [
        ("images", ("test1.jpg", image_data, "image/jpeg")),
        ("images", ("test2.jpg", image_data, "image/jpeg")),
    ]

    response = client.patch("/api/v1/company", files=files)
    
    assert response.status_code == 400
    assert "Total number of company images must be 10 or less" in response.json()['detail']
    mock_get_by_domain.assert_called_once()
    mock_save_image_to_destination.assert_not_called()

def test_get_company_by_domain_not_found():
    with mock.patch("app.models.company.Company.get_by_domain", return_value=None) as mock_get_by_domain:
        app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

        response = client.get("/api/v1/company", params={"domain": "unknown.com"})

        assert response.status_code == 404
        assert response.json()["detail"] == "Company not found"
        mock_get_by_domain.assert_called_once()