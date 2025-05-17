import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import base64
import json
import hmac
import hashlib

from tech.interfaces.gateways.cognito_gateway import CognitoGateway


class TestCognitoGateway:
    @pytest.fixture
    def cognito_gateway(self):
        with patch('boto3.client') as mock_client:
            # Mock das exceções do boto3
            mock_client.return_value.exceptions = MagicMock()

            # Configurar exceções específicas
            not_authorized_exception = type('NotAuthorizedException', (Exception,), {})
            user_not_found_exception = type('UserNotFoundException', (Exception,), {})

            mock_client.return_value.exceptions.NotAuthorizedException = not_authorized_exception
            mock_client.return_value.exceptions.UserNotFoundException = user_not_found_exception

            gateway = CognitoGateway()
            gateway.client = mock_client.return_value
            yield gateway

    def test_init(self):
        with patch('boto3.client') as mock_client:
            gateway = CognitoGateway()
            mock_client.assert_called_once()
            assert gateway.region == "us-east-1"
            assert gateway.user_pool_id == "us-east-1_k6nq9jjr3"
            assert gateway.client_id == "7krs58hvehmmanp97ig1h1lpqj"
            assert gateway.client_secret == "lvojlqtnr3q9pjee4g1k2rt1pm461a0rl4nsslk6ud5pt0il8am"

    def test_get_secret_hash(self, cognito_gateway):
        # Test secret hash generation
        username = "123456789"
        expected_message = username + cognito_gateway.client_id
        expected_dig = hmac.new(
            cognito_gateway.client_secret.encode('utf-8'),
            msg=expected_message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        expected_hash = base64.b64encode(expected_dig).decode()

        result = cognito_gateway._get_secret_hash(username)
        assert result == expected_hash

    def test_authenticate_success(self, cognito_gateway):
        # Mock successful authentication response
        mock_response = {
            "AuthenticationResult": {
                "AccessToken": "test-access-token",
                "IdToken": "test-id-token",
                "RefreshToken": "test-refresh-token",
                "ExpiresIn": 3600
            }
        }
        cognito_gateway.client.initiate_auth.return_value = mock_response

        # Test authentication
        result = cognito_gateway.authenticate("12345678900", "password123")

        # Verify the client was called with correct parameters
        cognito_gateway.client.initiate_auth.assert_called_once()
        call_args = cognito_gateway.client.initiate_auth.call_args[1]
        assert call_args["AuthFlow"] == "USER_PASSWORD_AUTH"
        assert call_args["ClientId"] == cognito_gateway.client_id
        assert call_args["AuthParameters"]["USERNAME"] == "12345678900"
        assert call_args["AuthParameters"]["PASSWORD"] == "password123"
        assert "SECRET_HASH" in call_args["AuthParameters"]

        # Verify the result
        assert result == mock_response["AuthenticationResult"]

    def test_authenticate_invalid_credentials(self, cognito_gateway):
        # Create a real exception instance
        not_auth_exception = cognito_gateway.client.exceptions.NotAuthorizedException()

        # Set side effect to raise exception
        cognito_gateway.client.initiate_auth.side_effect = not_auth_exception

        # Test authentication with invalid credentials
        with pytest.raises(ValueError) as excinfo:
            cognito_gateway.authenticate("12345678900", "wrong_password")

        assert "Incorrect credentials" in str(excinfo.value)

    def test_authenticate_user_not_found(self, cognito_gateway):
        # Create a real exception instance
        user_not_found_exception = cognito_gateway.client.exceptions.UserNotFoundException()

        # Set side effect to raise exception
        cognito_gateway.client.initiate_auth.side_effect = user_not_found_exception

        # Test authentication with non-existent user
        with pytest.raises(ValueError) as excinfo:
            cognito_gateway.authenticate("nonexistent", "password123")

        assert "User not found" in str(excinfo.value)

    def test_authenticate_other_error(self, cognito_gateway):
        # Mock other exception
        other_error = Exception("Some unexpected error")
        cognito_gateway.client.initiate_auth.side_effect = other_error

        # Test authentication with other error
        with pytest.raises(ValueError) as excinfo:
            cognito_gateway.authenticate("12345678900", "password123")

        assert "Authentication failed" in str(excinfo.value)

    def test_decode_jwt_manually_valid(self, cognito_gateway):
        # Create a simple test JWT
        payload = {"sub": "test-user", "email": "test@example.com"}
        encoded_payload = base64.b64encode(json.dumps(payload).encode()).decode()
        encoded_payload = encoded_payload.replace('+', '-').replace('/', '_').rstrip('=')
        test_jwt = f"header.{encoded_payload}.signature"

        # Test decoding
        result = cognito_gateway._decode_jwt_manually(test_jwt)
        assert result == payload

    def test_decode_jwt_manually_invalid_format(self, cognito_gateway):
        # Test with invalid JWT format
        with pytest.raises(ValueError) as excinfo:
            cognito_gateway._decode_jwt_manually("invalid-token")

        assert "Invalid JWT format" in str(excinfo.value)

    def test_verify_token_with_groups_in_token(self, cognito_gateway):
        # Create a test JWT with groups
        payload = {
            "sub": "test-user-id",
            "cognito:username": "test-user",
            "email": "test@example.com",
            "cognito:groups": ["admin", "users"]
        }
        encoded_payload = base64.b64encode(json.dumps(payload).encode()).decode()
        encoded_payload = encoded_payload.replace('+', '-').replace('/', '_').rstrip('=')
        test_jwt = f"header.{encoded_payload}.signature"

        # Test token verification
        result = cognito_gateway.verify_token(test_jwt)

        # Check result
        assert result["username"] == "test-user"
        assert result["attributes"]["sub"] == "test-user-id"
        assert result["attributes"]["email"] == "test@example.com"
        assert result["is_admin"] is True

    def test_verify_token_without_groups(self, cognito_gateway):
        # Create a test JWT without groups
        payload = {
            "sub": "test-user-id",
            "email": "test@example.com"
        }
        encoded_payload = base64.b64encode(json.dumps(payload).encode()).decode()
        encoded_payload = encoded_payload.replace('+', '-').replace('/', '_').rstrip('=')
        test_jwt = f"header.{encoded_payload}.signature"

        # Mock admin_get_user response
        cognito_gateway.client.admin_get_user.return_value = {
            "Username": "test-user-id",
            "UserAttributes": [
                {"Name": "sub", "Value": "test-user-id"},
                {"Name": "email", "Value": "test@example.com"}
            ]
        }

        # Mock admin_list_groups_for_user response
        cognito_gateway.client.admin_list_groups_for_user.return_value = {
            "Groups": [
                {"GroupName": "users"},
                {"GroupName": "admin"}
            ]
        }

        # Test token verification
        result = cognito_gateway.verify_token(test_jwt)

        # Verify client calls
        cognito_gateway.client.admin_get_user.assert_called_once_with(
            UserPoolId=cognito_gateway.user_pool_id,
            Username="test-user-id"
        )
        cognito_gateway.client.admin_list_groups_for_user.assert_called_once_with(
            UserPoolId=cognito_gateway.user_pool_id,
            Username="test-user-id"
        )

        # Check result
        assert result["username"] == "test-user-id"
        assert result["attributes"]["sub"] == "test-user-id"
        assert result["attributes"]["email"] == "test@example.com"
        assert result["is_admin"] is True

    def test_verify_token_user_not_found(self, cognito_gateway):
        # Create a test JWT
        payload = {"sub": "nonexistent-user"}
        encoded_payload = base64.b64encode(json.dumps(payload).encode()).decode()
        encoded_payload = encoded_payload.replace('+', '-').replace('/', '_').rstrip('=')
        test_jwt = f"header.{encoded_payload}.signature"

        # Configurar para lançar exceção
        user_not_found_exception = cognito_gateway.client.exceptions.UserNotFoundException()
        cognito_gateway.client.admin_get_user.side_effect = user_not_found_exception

        # Test verification with non-existent user
        with pytest.raises(ValueError) as excinfo:
            cognito_gateway.verify_token(test_jwt)

        assert "User not found" in str(excinfo.value)

    def test_verify_token_invalid_token(self, cognito_gateway):
        # Test with invalid token
        with pytest.raises(ValueError) as excinfo:
            cognito_gateway.verify_token("invalid-token")

        assert "Invalid JWT format" in str(excinfo.value)

    def test_verify_token_admin_status_error(self, cognito_gateway):
        # Create a test JWT
        payload = {"sub": "test-user-id"}
        encoded_payload = base64.b64encode(json.dumps(payload).encode()).decode()
        encoded_payload = encoded_payload.replace('+', '-').replace('/', '_').rstrip('=')
        test_jwt = f"header.{encoded_payload}.signature"

        # Mock admin_get_user response
        cognito_gateway.client.admin_get_user.return_value = {
            "Username": "test-user-id",
            "UserAttributes": []
        }

        # Mock error in admin_list_groups_for_user
        cognito_gateway.client.admin_list_groups_for_user.side_effect = Exception("Error checking groups")

        # Test verification with error in admin status check
        with pytest.raises(ValueError) as excinfo:
            cognito_gateway.verify_token(test_jwt)

        assert "Failed to verify admin status" in str(excinfo.value)

    def test_verify_token_no_username(self, cognito_gateway):
        # Create a test JWT without user identifier
        payload = {"email": "test@example.com"}
        encoded_payload = base64.b64encode(json.dumps(payload).encode()).decode()
        encoded_payload = encoded_payload.replace('+', '-').replace('/', '_').rstrip('=')
        test_jwt = f"header.{encoded_payload}.signature"

        # Test verification without user identifier
        with pytest.raises(ValueError) as excinfo:
            cognito_gateway.verify_token(test_jwt)

        assert "Token does not contain user identifier" in str(excinfo.value)