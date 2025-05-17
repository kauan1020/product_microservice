import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tech.infra.repositories.sql_alchemy_models import SQLAlchemyProduct, table_registry
from tech.infra.settings.settings import Settings
from tech.domain.value_objects import CPF
from tech.domain.security import get_password_hash, verify_password, get_cpf_hash, verify_cpf


class TestSQLAlchemyModels:
    @pytest.fixture
    def setup_database(self):
        # Create in-memory SQLite database for testing
        engine = create_engine("sqlite:///:memory:")
        table_registry.metadata.create_all(engine)
        with Session(engine) as session:
            yield session

    def test_sqlalchemy_product_creation(self, setup_database):
        session = setup_database

        # Create a product
        product = SQLAlchemyProduct(
            name="Test Product",
            price=10.99,
            category="Test Category"
        )

        # Add to session and commit
        session.add(product)
        session.commit()

        # Query and check
        saved_product = session.query(SQLAlchemyProduct).filter_by(name="Test Product").first()

        assert saved_product is not None
        assert saved_product.id is not None
        assert saved_product.name == "Test Product"
        assert saved_product.price == 10.99
        assert saved_product.category == "Test Category"
        assert isinstance(saved_product.created_at, datetime)
        assert isinstance(saved_product.updated_at, datetime)

    def test_sqlalchemy_product_update(self, setup_database):
        session = setup_database

        # Create a product
        product = SQLAlchemyProduct(
            name="Test Product",
            price=10.99,
            category="Test Category"
        )

        # Add to session and commit
        session.add(product)
        session.commit()

        # Store original update time
        original_updated_at = product.updated_at

        # Wait a bit to ensure timestamp difference
        import time
        time.sleep(0.1)

        # Update product
        product.price = 15.99
        session.commit()

        # Query and check
        updated_product = session.query(SQLAlchemyProduct).filter_by(id=product.id).first()

        assert updated_product.price == 15.99
        assert updated_product.updated_at > original_updated_at


class TestSettings:

    def test_settings_from_env(self):
        # Test with env variables
        test_db_url = "postgresql://user:pass@localhost/testdb"
        with patch.dict('os.environ', {"DATABASE_URL": test_db_url}):
            settings = Settings()
            assert settings.DATABASE_URL == test_db_url


class TestCPF:
    def test_valid_cpf_creation(self):
        cpf = CPF("12345678901")
        assert cpf.value == "12345678901"
        assert str(cpf) == "12345678901"

    def test_invalid_cpf_length(self):
        with pytest.raises(ValueError) as excinfo:
            CPF("1234567890")  # Too short
        assert "CPF must contain exactly 11 digits" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            CPF("123456789012")  # Too long
        assert "CPF must contain exactly 11 digits" in str(excinfo.value)

    def test_non_numeric_cpf(self):
        with pytest.raises(ValueError) as excinfo:
            CPF("1234567890a")
        assert "CPF must contain exactly 11 digits and be numeric" in str(excinfo.value)


class TestSecurity:
    @patch('tech.domain.security.pwd_context')
    def test_get_password_hash(self, mock_pwd_context):
        mock_pwd_context.hash.return_value = "hashed_password"

        result = get_password_hash("password123")

        mock_pwd_context.hash.assert_called_once_with("password123")
        assert result == "hashed_password"

    @patch('tech.domain.security.pwd_context')
    def test_verify_password(self, mock_pwd_context):
        mock_pwd_context.verify.return_value = True

        result = verify_password("password123", "hashed_password")

        mock_pwd_context.verify.assert_called_once_with("password123", "hashed_password")
        assert result is True

    @patch('tech.domain.security.pwd_context')
    def test_get_cpf_hash(self, mock_pwd_context):
        mock_pwd_context.hash.return_value = "hashed_cpf"

        result = get_cpf_hash("12345678901")

        mock_pwd_context.hash.assert_called_once_with("12345678901")
        assert result == "hashed_cpf"

    @patch('tech.domain.security.pwd_context')
    def test_verify_cpf(self, mock_pwd_context):
        mock_pwd_context.verify.return_value = True

        result = verify_cpf("12345678901", "hashed_cpf")

        mock_pwd_context.verify.assert_called_once_with("12345678901", "hashed_cpf")
        assert result is True


@pytest.mark.skip("Integration test that requires database connection")
class TestDatabaseConnection:
    def test_get_session(self):
        from tech.infra.databases.database import get_session

        session_generator = get_session()
        session = next(session_generator)

        assert isinstance(session, Session)

        # Clean up session
        try:
            next(session_generator)
        except StopIteration:
            pass