# tests/unit/use_cases/products/test_verify_token_use_case.py
import pytest
from unittest.mock import Mock, patch
from tech.interfaces.gateways.cognito_gateway import CognitoGateway
from tech.use_cases.products.verify_token_use_case import VerifyTokenUseCase


class TestVerifyTokenUseCase:
    """Unit tests for the VerifyTokenUseCase."""

    def setup_method(self):
        """Set up test dependencies."""
        # Create mock for the Cognito gateway
        self.cognito_gateway = Mock(spec=CognitoGateway)

        # Initialize the use case with the mock
        self.use_case = VerifyTokenUseCase(self.cognito_gateway)

        # Sample token and user data
        self.valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"
        self.user_data = {
            "username": "test_user",
            "attributes": {
                "sub": "user-sub-id",
                "email": "test@example.com"
            },
            "is_admin": True
        }

    def test_verify_valid_token(self):
        """Test verification of a valid token."""
        # Arrange
        self.cognito_gateway.verify_token.return_value = self.user_data

        # Act
        result = self.use_case.execute(self.valid_token)

        # Assert
        self.cognito_gateway.verify_token.assert_called_once_with(self.valid_token)
        assert result == self.user_data
        assert result["is_admin"] is True
        assert result["username"] == "test_user"

    def test_verify_token_invalid_token(self):
        """Test verification with an invalid token throws the appropriate exception."""
        # Arrange
        error_message = "Invalid token format"
        self.cognito_gateway.verify_token.side_effect = ValueError(error_message)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(self.valid_token)

        # Verify error message and that the gateway was called
        assert error_message in str(exc_info.value)
        self.cognito_gateway.verify_token.assert_called_once_with(self.valid_token)

    def test_verify_token_user_not_found(self):
        """Test verification when the user is not found."""
        # Arrange
        error_message = "User not found"
        self.cognito_gateway.verify_token.side_effect = ValueError(error_message)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(self.valid_token)

        # Verify error message and that the gateway was called
        assert error_message in str(exc_info.value)
        self.cognito_gateway.verify_token.assert_called_once_with(self.valid_token)

    def test_verify_token_expired(self):
        """Test verification with an expired token."""
        # Arrange
        error_message = "Token has expired"
        self.cognito_gateway.verify_token.side_effect = ValueError(error_message)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(self.valid_token)

        # Verify error message and that the gateway was called
        assert error_message in str(exc_info.value)
        self.cognito_gateway.verify_token.assert_called_once_with(self.valid_token)

    def test_verify_token_unexpected_error(self):
        """Test verification with an unexpected error."""
        # Arrange
        error_message = "Unexpected error occurred"
        self.cognito_gateway.verify_token.side_effect = Exception(error_message)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.use_case.execute(self.valid_token)

        # Verify error message and that the gateway was called
        assert error_message in str(exc_info.value)
        self.cognito_gateway.verify_token.assert_called_once_with(self.valid_token)

    def test_verify_token_with_empty_token(self):
        """Test verification with an empty token."""
        # Arrange
        empty_token = ""
        error_message = "Token cannot be empty"
        self.cognito_gateway.verify_token.side_effect = ValueError(error_message)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(empty_token)

        # Verify error message and that the gateway was called
        assert error_message in str(exc_info.value)
        self.cognito_gateway.verify_token.assert_called_once_with(empty_token)

    @patch('builtins.print')
    def test_verify_token_prints_debugging_info(self, mock_print):
        """Test that the use case prints debugging information."""
        # Arrange
        self.cognito_gateway.verify_token.return_value = self.user_data

        # Act
        self.use_case.execute(self.valid_token)

        # Assert that debugging information was printed
        assert mock_print.call_count == 2

        # First print should contain the token prefix
        first_call_args = mock_print.call_args_list[0][0][0]
        assert "Attempting to verify token:" in first_call_args
        assert self.valid_token[:10] in first_call_args

        # Second print should contain the user data
        second_call_args = mock_print.call_args_list[1][0][0]
        assert "Token verified successfully" in second_call_args
        assert "user data:" in second_call_args

    @patch('builtins.print')
    def test_verify_token_prints_error_info(self, mock_print):
        """Test that the use case prints error information when verification fails."""
        # Arrange
        error_message = "Invalid token format"
        self.cognito_gateway.verify_token.side_effect = ValueError(error_message)

        # Act & Assert
        with pytest.raises(ValueError):
            self.use_case.execute(self.valid_token)

        # Assert that error information was printed
        assert mock_print.call_count == 2

        # First print should contain the token prefix
        first_call_args = mock_print.call_args_list[0][0][0]
        assert "Attempting to verify token:" in first_call_args

        # Second print should contain the error message
        second_call_args = mock_print.call_args_list[1][0][0]
        assert "Token verification failed:" in second_call_args
        assert error_message in second_call_args