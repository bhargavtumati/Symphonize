import io

from unittest import mock

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.master_data import MasterData
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

@mock.patch("app.models.master_data.MasterData.create", return_value=None)
@mock.patch("app.models.master_data.MasterData.get_existing_record", return_value=None)
@mock.patch("app.models.master_data.MasterData.get_all_by_type", return_value=[("IT",),("Healthcare",)])
def test_add_new_industry_type_success(mock_get_all, mock_get_existing, mock_create):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/industry-type", json={"industry_type": "Healthcare"})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Industry type added successfully"
    mock_create.assert_called_once()
    mock_get_existing.assert_called_once()
    mock_get_all.called_once()

@mock.patch("app.models.master_data.MasterData.create", return_value=None)
@mock.patch("app.models.master_data.MasterData.get_existing_record", return_value=mock.MagicMock(id=1))
def test_add_new_industry_type_duplicte(mock_get_existing, mock_create):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/industry-type", json={"industry_type": "Healthcare"})
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_get_existing.assert_called_once()

def test_add_new_industry_type_pydantic_error():
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/industry-type", json={"industry_type": ""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@mock.patch("app.models.master_data.MasterData.get_existing_record", side_effect=Exception("DB Error"))
def test_add_new_industry_type_db_error(mock_get_existing_record):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/industry-type", json={"industry_type": "Healthcare"})

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error during database call" in response.json()["detail"]
    mock_get_existing_record.assert_called_once()

@mock.patch("app.models.master_data.MasterData.get_all_by_type", return_value=[["Healthcare"], ["Finance"]])
def test_get_all_industry_types_success(mock_get_all):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.get("api/v1/company/industry-types")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["industry_types"] == ["Healthcare", "Finance"]
    mock_get_all.assert_called_once()

@mock.patch("app.models.master_data.MasterData.get_all_by_type", side_effect=Exception("DB Error")) 
def test_get_all_industry_types_db_error(mock_get_all):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.get("api/v1/company/industry-types")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error during database call" in response.json()["detail"]
    mock_get_all.assert_called_once()

@mock.patch("app.models.master_data.MasterData.create", return_value=None)
@mock.patch("app.models.master_data.MasterData.get_existing_record", return_value=None)
@mock.patch("app.models.master_data.MasterData.get_all_by_type", return_value=[("IT",),("Healthcare",)])
def test_add_new_department_success(mock_get_all, mock_get_existing, mock_create):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/department", json={"department": "IT"})
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Department added successfully"
    mock_create.assert_called_once()
    mock_get_existing.assert_called_once()
    mock_get_all.called_once()

def test_add_new_department_pydantic_error():
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/department", json={"department": ""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@mock.patch("app.models.master_data.MasterData.get_existing_record", side_effect=Exception("DB Error"))
def test_add_new_department_db_error(mock_get_existing_record):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/department", json={"department": "IT"})

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error during database call" in response.json()["detail"]
    mock_get_existing_record.assert_called_once()

@mock.patch("app.models.master_data.MasterData.get_all_by_type", return_value=[["IT"], ["Healthcare"]])
def test_get_all_departments_success(mock_get_all):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.get("api/v1/company/departments")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["departments"] == ["IT", "Healthcare"]
    mock_get_all.assert_called_once()

@mock.patch("app.models.master_data.MasterData.get_all_by_type", side_effect=Exception("DB Error")) 
def test_get_all_departments_db_error(mock_get_all):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.get("api/v1/company/departments")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error during database call" in response.json()["detail"]
    mock_get_all.assert_called_once()


#test cases for designation endpoints
@mock.patch("app.models.master_data.MasterData.create", return_value=None)
@mock.patch("app.models.master_data.MasterData.get_existing_record", return_value=None)
@mock.patch("app.models.master_data.MasterData.get_all_designations", return_value=[("Manager",),("Software Engineer",), ("Associate Software Engineer",)])
def test_add_new_designation_success(mock_get_all, mock_get_existing, mock_create):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/designation", json={"designation": "Associate Software Engineer"})   
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Designation added successfully"
    mock_create.assert_called_once()
    mock_get_existing.assert_called_once()
    mock_get_all.called_once()


def test_add_new_designation_pydantic_error():
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/designation", json={"designation": ""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@mock.patch("app.models.master_data.MasterData.get_existing_record", return_value=None)
@mock.patch("app.models.master_data.MasterData.create", side_effect=Exception("DB Error"))
def test_add_new_designation_db_error(mock_get_existing, mock_create):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/designation", json={"designation": "IT"})

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error during database call" in response.json()["detail"]
    mock_create.assert_called_once()
    mock_get_existing.assert_called_once()


@mock.patch("app.models.master_data.MasterData.get_existing_record", return_value=mock.MagicMock(id=1))
@mock.patch("app.models.master_data.MasterData.create", side_effect=Exception("DB Error"))
def test_add_new_designation_duplicate_name(mock_create, mock_get_existing):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.post("api/v1/company/designation", json={"designation": "IT"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Designation already exists" in response.json()["detail"]
    mock_get_existing.assert_called_once()


@mock.patch("app.models.master_data.MasterData.get_all_designations", return_value=[["Associate Software Engineer"], ["Manager"], ["Software Engineer"]])
def test_get_all_designations_success(mock_get_all):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.get("api/v1/company/designations")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["designations"] == ["Associate Software Engineer", "Manager", "Software Engineer"]
    mock_get_all.assert_called_once()

@mock.patch("app.models.master_data.MasterData.get_all_designations", side_effect=Exception("DB Error")) 
def test_get_all_designations_db_error(mock_get_all):
    app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token
    response = client.get("api/v1/company/designations")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error during database call" in response.json()["detail"]
    mock_get_all.assert_called_once()