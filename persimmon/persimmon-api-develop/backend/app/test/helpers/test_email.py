import unittest
from unittest.mock import patch, MagicMock
from fastapi import UploadFile
from io import BytesIO

class TestSendEmail(unittest.TestCase):
    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        from app.helpers.email_helper import send_email

        # Create a mock SMTP instance
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        # Mock methods to return as expected
        mock_smtp_instance.starttls.return_value = None
        mock_smtp_instance.login.return_value = None
        mock_smtp_instance.sendmail.return_value = None

        # Prepare mock attachment
        attachment_mock = [UploadFile(filename="test.txt", file=BytesIO(b"Test file content"))]

        # Call the send_email function
        result = send_email(
            subject="Test Email",
            body="Hello {{name}}",
            to_email="test@example.com",
            from_email="sender@example.com",
            reply_to_email="reply@example.com",
            template_data={"name": "John"},
            attachment=attachment_mock,
        )

        # **Assertions & Debugging**
        print("Result:", result)

        # Print the calls to sendmail to see what's happening
        print("Mock SMTP instance calls:", mock_smtp_instance.mock_calls)

        # Ensure the context manager calls are in the right order
        self.assertTrue(mock_smtp_instance.__enter__.called, "__enter__ was not called.")
        self.assertTrue(mock_smtp_instance.__exit__.called, "__exit__ was not called.")

        # Check if sendmail was called inside the context manager
        sendmail_called = any("sendmail" in str(call) for call in mock_smtp_instance.mock_calls)
        self.assertTrue(sendmail_called, "sendmail was not called within the context manager.")

        # Access the sendmail call arguments safely
        sendmail_call = mock_smtp_instance.sendmail.call_args
        if sendmail_call:
            # Ensure sendmail was called with the expected arguments
            self.assertEqual(sendmail_call[0][0], "sender@example.com")  # from_email
            self.assertEqual(sendmail_call[0][1], "test@example.com")    # to_email

        # Verify the result message
        self.assertIn("Email sent successfully", result)

if __name__ == "__main__":
    unittest.main()