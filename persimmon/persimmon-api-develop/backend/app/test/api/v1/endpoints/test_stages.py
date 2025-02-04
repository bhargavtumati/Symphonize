import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.helpers.firebase_helper import verify_firebase_token

client = TestClient(app)

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"
    }

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token

@patch("app.models.stages.Stages.get_by_id")
def test_get_stages(mock_get_stages):
    mock_stages_instance = MagicMock()
    mock_stages_instance.stages = [
        {"uuid": "cd81dcf2-3d6a-492l-96k4-87782271079q", "name": "Interviewing"},
        {"uuid": "zm82dcf2-3h6a-492l-96k4-87782271079q", "name": "Deployed"},
        {"uuid": "md81dcf2-3d6a-492l-96k4-87782271079q", "name": "Rejected"}
    ]
    mock_get_stages.return_value = mock_stages_instance

    job_id = 1
    response = client.get(f"/api/v1/stages?job_id={job_id}")

    assert response.status_code == 200
    assert response.json() == {
        "stages": [
            {"uuid": "zm82dcf2-3h6a-492l-96k4-87782271079q", "name": "Deployed"},
            {"uuid": "md81dcf2-3d6a-492l-96k4-87782271079q", "name": "Rejected"}
        ],
        "message": "Stages list retrieved successfully",
        "status": 200
    }
