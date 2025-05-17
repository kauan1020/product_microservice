import os
import sys
import pytest
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


@pytest.fixture
def mock_db_session():
    """
    Fornece uma sessão de banco de dados mockada para testes.
    Em testes de integração, podemos usar um banco de dados de teste real
    ou continuar usando mocks, dependendo do contexto.
    """
    session = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    yield session


# Mock para cliente MongoDB
@pytest.fixture
def mock_mongodb_client():
    """
    Fornece um cliente MongoDB mockado para testes.
    Em testes de integração, podemos usar um MongoDB de teste real
    ou continuar usando mocks, dependendo do contexto.
    """
    client = Mock()
    db = Mock()
    collection = Mock()

    client.get_database.return_value = db
    db.get_collection.return_value = collection

    yield client


@pytest.fixture
def mock_cognito_gateway():
    """
    Fornece um CognitoGateway mockado para testes.
    """
    from tech.interfaces.gateways.cognito_gateway import CognitoGateway

    gateway = Mock(spec=CognitoGateway)
    gateway.authenticate.return_value = {
        "IdToken": "mock-jwt-token",
        "ExpiresIn": 3600
    }
    gateway.verify_token.return_value = {
        "username": "test_user",
        "is_admin": True,
        "attributes": {
            "sub": "user-sub-id",
            "email": "test@example.com"
        }
    }

    yield gateway


# Utilitário para criar token JWT válido para testes
@pytest.fixture
def create_test_token():
    """
    Função utilitária para criar um token JWT falso para testes.
    """
    import time
    import jwt

    def _create_token(username="testuser", is_admin=False, expiry=3600):
        now = int(time.time())
        payload = {
            "sub": "test-user-id",
            "cognito:username": username,
            "cognito:groups": ["admin"] if is_admin else [],
            "exp": now + expiry,
            "iat": now,
            "email": f"{username}@example.com"
        }
        return jwt.encode(payload, "test-secret-key", algorithm="HS256")

    return _create_token

