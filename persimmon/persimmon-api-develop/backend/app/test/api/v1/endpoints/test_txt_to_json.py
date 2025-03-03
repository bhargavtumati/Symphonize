import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from app.main import app  # Replace with your FastAPI app's import path
from app.api.v1.endpoints.ai import text_to_json  # Replace with your actual path
from pydantic import BaseModel


class TextToJsonRequest(BaseModel):
    source: str
    uuid: str


@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_session():
    return Mock()

@pytest.fixture
def mock_verify_firebase_token():
    return {"email": "testuser@example.com"}

@pytest.fixture
def mock_security():
    return Mock(credentials="mock_token")

@pytest.fixture
def mock_get_base_url():
    return "http://localhost:8000"

@pytest.fixture
def mock_pubsub():
    mock = AsyncMock()
    mock.send_message_to_pubsub.return_value = "Message sent"
    return mock

@pytest.fixture
def mock_applicant():
    mock = Mock()
    mock.get_by_uuid = Mock(return_value=None)
    mock.update = Mock()
    return mock

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.ai.aih.extract_features_from_resume", new_callable=AsyncMock)
@patch("app.api.v1.endpoints.ai.gcph", new_callable=Mock)
@patch("app.api.v1.endpoints.ai.Applicant", new_callable=Mock)
async def test_text_to_json_success(
    mock_applicant_class,
    mock_pubsub,
    mock_extract_features,
    client,
    mock_session,
    mock_verify_firebase_token,
    mock_security,
    mock_get_base_url,
):
    mock_extract_features.return_value = '{"key": "value"}'
    mock_applicant_instance = Mock()
    mock_applicant_instance.get_by_uuid.return_value = mock_applicant_instance
    mock_applicant_class.get_by_uuid = mock_applicant_instance.get_by_uuid

    response = await text_to_json(
        TextToJsonRequest(source="/path/to/test.txt", uuid="test-uuid"),
        session=mock_session,
        credentials=mock_security,
        token=mock_verify_firebase_token,
        base_url=mock_get_base_url,
    )

    assert response["status"] == "success"
    assert "generated_json" in response
    assert "destination" in response

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.ai.text_to_json.aih.extract_features_from_resume", new_callable=AsyncMock)
async def test_text_to_json_rate_limit(mock_extract_features, client):
    mock_extract_features.side_effect = Exception("429 Too Many Requests")

    with pytest.raises(Exception, match="429 Too Many Requests"):
        await text_to_json(
            TextToJsonRequest(source="/path/to/test.txt", uuid="test-uuid"),
            session=Mock(),
            credentials=Mock(),
            token={"email": "testuser@example.com"},
            base_url="http://localhost:8000",
        )

@pytest.mark.asyncio
async def test_text_to_json_file_not_found(client):
    with pytest.raises(FileNotFoundError):
        await text_to_json(
            TextToJsonRequest(source="/invalid/path.txt", uuid="test-uuid"),
            session=Mock(),
            credentials=Mock(),
            token={"email": "testuser@example.com"},
            base_url="http://localhost:8000",
        )

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.ai.text_to_json.Applicant.get_by_uuid", return_value=None)
async def test_text_to_json_applicant_not_found(mock_get_by_uuid, client):
    with pytest.raises(Exception, match="Applicant was not found"):
        await text_to_json(
            TextToJsonRequest(source="/path/to/test.txt", uuid="test-uuid"),
            session=Mock(),
            credentials=Mock(),
            token={"email": "testuser@example.com"},
            base_url="http://localhost:8000",
        )
