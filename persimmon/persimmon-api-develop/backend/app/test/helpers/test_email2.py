import pytest 
from unittest.mock import Mock, MagicMock,patch
from fastapi.testclient import TestClient
from app.helpers import email_helper as emailh




@patch("app.helpers.email_helper.send_email")
def test_send_email(mock_send_email):
    mock_send_email.result_value = {}
     
    result = emailh.send_email(
        subject= "this is the subject",
        body = "tis is body",
        to_email= "gvkartheek@gmail.com",
        from_email = "carreers@gmail.com",
        reply_to_email= "xyz@gmail.com"
     )

    assert result  == {}
