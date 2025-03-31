import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.email import send_verification_email


@patch("app.email.SendGridAPIClient")
def test_send_verification_email_success(mock_sendgrid_client):
    mock_instance = MagicMock()
    mock_instance.send.return_value.status_code = 202
    mock_sendgrid_client.return_value = mock_instance

    # Should not raise any exceptions
    send_verification_email("test@example.com", "test-token")

    mock_instance.send.assert_called_once()


@patch("app.email.SendGridAPIClient")
def test_send_verification_email_failure_status(mock_sendgrid_client):
    mock_instance = MagicMock()
    mock_instance.send.return_value.status_code = 400
    mock_sendgrid_client.return_value = mock_instance

    with pytest.raises(HTTPException) as exc_info:
        send_verification_email("test@example.com", "test-token")

    assert exc_info.value.status_code == 500
    assert "Email failed to send" in str(exc_info.value.detail)


@patch("app.email.SendGridAPIClient", side_effect=Exception("SendGrid error"))
def test_send_verification_email_exception(mock_sendgrid_client):
    with pytest.raises(HTTPException) as exc_info:
        send_verification_email("test@example.com", "test-token")

    assert exc_info.value.status_code == 500
    assert "Email error: SendGrid error" in str(exc_info.value.detail)
