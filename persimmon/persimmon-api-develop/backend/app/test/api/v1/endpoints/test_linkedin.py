import pytest
from httpx import AsyncClient, HTTPStatusError, RequestError  
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from fastapi.testclient import TestClient
from app.helpers.firebase_helper import verify_firebase_token


client = TestClient(app)

def mock_verify_firebase_token():
    return {
        "user_id": "111",
        "email": "surendra.goluguri@symphonize.com"
    }

app.dependency_overrides[verify_firebase_token] = mock_verify_firebase_token


def sample_linkedin_payload():
    return {
    "author": "urn:li:person:cCGJRLg1gh",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "🚀 We are hiring! Check out this amazing job opportunity: https://persimmon-app-dev-793571778940.asia-south1.run.app/connection/symphonize.com/jobs?jobCode=Sym0071"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}




# @pytest.mark.asyncio
@patch("app.helpers.linkedin_helper.fetch_access_token")
def test_get_access_token(mock_fetch_access_token):
    mock_fetch_access_token.return_value = {"access_token": "mock_access_token"}
    response = client.post("api/v1/linkedin/access-token/", json={"code": "mock_code"})
    assert response.status_code == 200
    assert response.json() == {"access_token": "mock_access_token"}

# @pytest.mark.asyncio
@patch("app.helpers.linkedin_helper.fetch_linkedin_profile")
def test_get_linkedin_profile(mock_fetch_linkedin_profile):
    mock_fetch_linkedin_profile.return_value = {"profile": "mock_profile_data"}
    response = client.get("api/v1/linkedin/profile/", params={"access_token": "mock_access_token"})
    assert response.status_code == 200
    assert response.json() == {"profile": "mock_profile_data"}




# import pytest
# from unittest.mock import patch, AsyncMock, MagicMock
# from fastapi.testclient import TestClient
# from app.main import app  # Assuming your FastAPI app instance is named `app`

# client = TestClient(app)

# Sample payload as per your provided structure



# @pytest.mark.asyncio
# @patch("app.helpers.linkedin_helper.get_linkedin_headers", new_callable=AsyncMock)
# @patch("httpx.AsyncClient.post", new_callable=AsyncMock)
# async def test_post_linkedin_job_success(mock_post, mock_get_linkedin_headers):
#     # Mock Headers for LinkedIn API
#     mock_get_linkedin_headers.return_value = {
#         "Authorization": "Bearer mock_access_token",
#         "Content-Type": "application/json",
#         "X-Restli-Protocol-Version": "2.0.0"
#     }

#     # Mock Successful LinkedIn Post Response
#     mock_post.return_value.status_code = 201
#     mock_post.return_value.json.return_value = {"id": "mock_post_id"}

#     # Correct endpoint path
#     response = client.post(
#         "api/v1/linkedin/post-job/",
#         json=sample_linkedin_payload,
#         params={"access_token": "mock_access_token"}
#     )

#     assert response.status_code == 200
#     assert response.json() == {
#         "message": "Job post successfully created",
#         "response_data": {"id": "mock_post_id"}
#     }



# @pytest.mark.asyncio
def test_post_linkedin_job_success():
    # Mock dependencies
    mock_headers = {
        "Authorization": "Bearer mock_access_token",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    # Use proper async mocking
    with (
        patch("app.helpers.firebase_helper.verify_firebase_token") as mock_auth,
        patch("app.helpers.linkedin_helper.get_linkedin_headers") as mock_headers_func,
        patch("httpx.AsyncClient.post") as mock_post
    ):
        # Setup mocks
        mock_auth.return_value = {"user_id": "test_user"}
        mock_headers_func.return_value = mock_headers
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "mock_post_id"}
        mock_post.return_value = mock_response

        # Make request
        response = client.post(
            "api/v1/linkedin/post-job/",
            json= {
                    "content": {
                    "author": "urn:li:person:cCGJRLg1gh",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": "We are hiring! Check out this amazing job opportunity: https://persimmon-app-dev-793571778940.asia-south1.run.app/connection/symphonize.com/jobs?jobCode=Sym0071"
                            },
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
            },
            params={"access_token": "test_token"},  # Query parameter
        )

        # Verify response
        assert response.status_code == 200
        assert response.json() == {
            "message": "Job post successfully created",
            "response_data": {"id": "mock_post_id"}
        }
        
# @pytest.mark.asyncio
def test_post_linkedin_job_success_one():
    # Mock dependencies
    mock_headers = {
        "Authorization": "Bearer mock_access_token",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    # Use proper async mocking 
    with (
        patch("app.helpers.firebase_helper.verify_firebase_token") as mock_auth,
        patch("app.helpers.linkedin_helper.get_linkedin_headers") as mock_headers_func,
        patch("httpx.AsyncClient.post") as mock_post
    ):
        # Setup mocks
        mock_auth.return_value = {"user_id": "test_user"}
        mock_headers_func.return_value = mock_headers
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "mock_post_id"}
        mock_post.return_value = mock_response

        # Make request with correct parameters
        response = client.post(
             "api/v1/linkedin/post-job/",
            json= {
                "content": {  # This matches LinkedInPostPayload structure
                    "author": "urn:li:person:cCGJRLg1gh",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": "Test job posting"
                            },
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
            },
            params={"access_token": "test_token"}  # Add required query parameter
        )

        # Verify response
        assert response.status_code == 200
        assert response.json() == {
            "message": "Job post successfully created",
            "response_data": {"id": "mock_post_id"}
        }
        