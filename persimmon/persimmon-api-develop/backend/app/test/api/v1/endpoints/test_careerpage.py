from io import BytesIO
from PIL import Image
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.helpers.firebase_helper import verify_firebase_token

# Override the dependency to mock the firebase token verification
def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"  # Ensure the email matches the domain
    }

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

client = TestClient(app)

@patch("app.api.v1.endpoints.careerpage.Customization.get_customization_settings")
@patch("app.api.v1.endpoints.careerpage.Company.get_by_domain")
def test_get_customization_settings(mock_get_company, mock_get_customization_settings):
    # Mock company and customization settings
    mock_get_company.return_value = MagicMock(id=1, domain="symphonize.com")
    mock_get_customization_settings.return_value = MagicMock(settings={})

    # Send GET request to the endpoint
    response = client.get("/api/v1/careerpage/extract-settings/domain/symphonize")

    # Assertions
    assert response.status_code == 200
    assert response.json()["message"] == "Settings data retrieved successfully"


@patch("app.api.v1.endpoints.careerpage.Customization.get_customization_settings")
@patch("app.api.v1.endpoints.careerpage.Company.get_by_domain")
def test_create_or_update_customization(mock_get_company, mock_get_customization_settings):
    # Mock the company data and return an empty customization settings dictionary
    mock_get_company.return_value = MagicMock(id=1, domain="symphonize.com")  # Ensure domain matches
    mock_get_customization_settings.return_value = MagicMock(settings={})

    # Define the form data to simulate the form fields that would be sent by the client
    form_data = {
        "career_page_url": "https://careers.symphonize.com",  # Update to match domain
        "enable_cover_photo": "true",  # Since this is a form, it's passed as a string
        "heading": "Join Us",
        "description": "Join our team!",
        "enable_dark_mode": "false",  # Passed as string to match form handling
        "color_selected": "blue",
        "primary_colors": '["red", "blue"]',
        "header_colors": '["green", "yellow"]',
        "font_style": "Arial",
    }

    # ✅ Create valid JPEG image using PIL
    image_file = BytesIO()
    image = Image.new("RGB", (100, 100), color="red")
    image.save(image_file, format="JPEG")
    image_file.name = "image.jpg"
    image_file.seek(0)

    # ✅ Create valid PNG icon using PIL
    icon_file = BytesIO()
    icon = Image.new("RGB", (50, 50), color="blue")
    icon.save(icon_file, format="PNG")
    icon_file.name = "icon.png"
    icon_file.seek(0)

    # Send POST request to the endpoint with mock image and icon files
    response = client.post(
        "/api/v1/careerpage/customization/domain/symphonize",  # Update the URL to match the domain
        data=form_data,  # Send as form data
        files={
            "image": (image_file.name, image_file, "image/jpeg"),
            "icon": (icon_file.name, icon_file, "image/png"),
        },
    )

    # Print response for debugging
    print(response.json())

    # Assertions to verify the response
    assert response.status_code == 200
    assert response.json()["message"] == "Customization settings created/modified successfully"


@patch("app.api.v1.endpoints.careerpage.Customization.get_customization_settings")
@patch("app.api.v1.endpoints.careerpage.Company.get_by_domain")
def test_domain(mock_get_company, mock_get_customization_settings):
    # Mock the company data and return an empty customization settings dictionary
    mock_get_company.return_value = MagicMock(id=1, domain="symphonize.com")  # Ensure domain matches
    mock_get_customization_settings.return_value = MagicMock(settings={})

    # Define the form data to simulate the form fields that would be sent by the client
    form_data = {
        "career_page_url": "https://careers.symphonize.com",  # Update to match domain
        "enable_cover_photo": "true",  # Since this is a form, it's passed as a string
        "heading": "Join Us",
        "description": "Join our team!",
        "enable_dark_mode": "false",  # Passed as string to match form handling
        "color_selected": "blue",
        "primary_colors": '["red", "blue"]',
        "header_colors": '["green", "yellow"]',
        "font_style": "Arial",
    }

    # ✅ Create valid JPEG image using PIL
    image_file = BytesIO()
    image = Image.new("RGB", (100, 100), color="red")
    image.save(image_file, format="JPEG")
    image_file.name = "image.jpg"
    image_file.seek(0)

    # ✅ Create valid PNG icon using PIL
    icon_file = BytesIO()
    icon = Image.new("RGB", (50, 50), color="blue")
    icon.save(icon_file, format="PNG")
    icon_file.name = "icon.png"
    icon_file.seek(0)

    # Send POST request to the endpoint with mock image and icon files
    response = client.post(
        "/api/v1/careerpage/customization/domain/tataconsultancy",  # Update the URL to match the domain
        data=form_data,  # Send as form data
        files={
            "image": (image_file.name, image_file, "image/jpeg"),
            "icon": (icon_file.name, icon_file, "image/png"),
        },
    )

    # Print response for debugging
    print(response.json())

    # Assertions to verify the response
    assert response.status_code == 403
    assert response.json()["detail"] == "Access Denied"
