# tests/unit/interfaces/middlewares/test_admin_auth_middleware.py
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from tech.interfaces.middlewares.admin_auth_middleware import admin_required


class TestAdminRequired:
    """Unit tests for the admin_required middleware."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        self.mock_credentials.credentials = "valid-token"

    @patch("tech.interfaces.middlewares.admin_auth_middleware.VerifyTokenUseCase")
    @patch("tech.interfaces.middlewares.admin_auth_middleware.CognitoGateway")
    def test_admin_access_allowed(self, mock_cognito_class, mock_verify_class):
        """Test that admin users are allowed access."""
        # Arrange
        mock_cognito_instance = Mock()
        mock_verify_instance = Mock()

        # Configure mocks to be returned when instantiated
        mock_cognito_class.return_value = mock_cognito_instance
        mock_verify_class.return_value = mock_verify_instance

        # Configure the mock token verification to return admin user data
        mock_verify_instance.execute.return_value = {
            "username": "admin_user",
            "is_admin": True
        }

        # Act
        result = admin_required(self.mock_credentials)

        # Assert
        # Check that the token was verified with correct token
        mock_verify_instance.execute.assert_called_once_with(self.mock_credentials.credentials)

        # Check that access was granted
        assert result is True

    @patch("tech.interfaces.middlewares.admin_auth_middleware.VerifyTokenUseCase")
    @patch("tech.interfaces.middlewares.admin_auth_middleware.CognitoGateway")
    def test_invalid_token(self, mock_cognito_class, mock_verify_class):
        """Test that invalid tokens raise a 401 Unauthorized exception."""
        # Arrange
        mock_cognito_instance = Mock()
        mock_verify_instance = Mock()

        # Configure mocks to be returned when instantiated
        mock_cognito_class.return_value = mock_cognito_instance
        mock_verify_class.return_value = mock_verify_instance

        # Configure token verification to fail
        mock_verify_instance.execute.side_effect = ValueError("Invalid token format")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_required(self.mock_credentials)

        # Verify exception details
        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in exc_info.value.detail

        # Verify token verification was attempted
        mock_verify_instance.execute.assert_called_once_with(self.mock_credentials.credentials)

    def test_missing_credentials(self):
        """Test that missing credentials raise a 401 Unauthorized exception."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_required(None)

        # Verify exception details
        assert exc_info.value.status_code == 401
        assert "Authentication credentials not provided" in exc_info.value.detail

    @patch("tech.interfaces.middlewares.admin_auth_middleware.VerifyTokenUseCase")
    @patch("tech.interfaces.middlewares.admin_auth_middleware.CognitoGateway")
    def test_empty_token(self, mock_cognito_class, mock_verify_class):
        """Test that empty tokens raise a validation error."""
        # Arrange
        self.mock_credentials.credentials = ""

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_required(self.mock_credentials)

        # Verify exception details
        assert exc_info.value.status_code == 401
        assert "Token must be a non-empty string" in exc_info.value.detail

        # Verify the verification was not attempted with empty token
        mock_verify_class.return_value.execute.assert_not_called()

    @patch("tech.interfaces.middlewares.admin_auth_middleware.VerifyTokenUseCase")
    @patch("tech.interfaces.middlewares.admin_auth_middleware.CognitoGateway")
    def test_general_exception(self, mock_cognito_class, mock_verify_class):
        """Test that general exceptions are handled properly."""
        # Arrange
        mock_cognito_instance = Mock()
        mock_verify_instance = Mock()

        # Configure mocks to be returned when instantiated
        mock_cognito_class.return_value = mock_cognito_instance
        mock_verify_class.return_value = mock_verify_instance

        # Configure a general exception during verification
        mock_verify_instance.execute.side_effect = Exception("Unexpected error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            admin_required(self.mock_credentials)

        # Verify exception details
        assert exc_info.value.status_code == 401
        assert "Authentication error" in exc_info.value.detail

        # Verify token verification was attempted
        mock_verify_instance.execute.assert_called_once_with(self.mock_credentials.credentials)