from unittest.mock import Mock, MagicMock,patch
from app.helpers import email_helper as emailh




@patch("app.helpers.email_helper.send_email")
def test_send_email(mock_send_email):
    mock_send_email.return_value = "Email sent successfully to gvkartheek@gmail.com!"
     
    result = emailh.send_email(
        subject= "this is the subject",
        body = "tis is body",
        to_email= "gvkartheek@gmail.com",
        from_email = "carreers@gmail.com",
        reply_to_email= "xyz@gmail.com"
     )

    assert result  == "Email sent successfully to gvkartheek@gmail.com!"
