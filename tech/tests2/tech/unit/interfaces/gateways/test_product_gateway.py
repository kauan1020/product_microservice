import pytest
from unittest.mock import Mock, patch
from tech.domain.entities.products import Products
from tech.interfaces.gateways.product_gateway import ProductGateway
from tech.infra.repositories.mongodb_product_repository import MongoDBProductRepository


class TestProductGateway:
    """Unit tests for the ProductGateway."""

    def setup_method(self):
        """Set up test dependencies."""
        # Create mock repository
        self.mock_repository = Mock(spec=MongoDBProductRepository)

        # Create mock product
        self.mock_product = Mock(spec=Products)
        self.mock_product.id = 1
        self.mock_product.name = "Test Product"
        self.mock_product.price = 10.99
        self.mock_product.category = "test_category"

        # Patch the MongoDBProductRepository initialization
        with patch('tech.interfaces.gateways.product_gateway.MongoDBProductRepository') as mock_repo_class:
            mock_repo_class.return_value = self.mock_repository
            self.gateway = ProductGateway()

        # Verify repository was initialized
        # Note: No session parameter here since MongoDB doesn't use SQLAlchemy sessions

    def test_add_product(self):
        """Test that add method delegates to repository correctly."""
        # Arrange
        self.mock_repository.add.return_value = self.mock_product

        # Act
        result = self.gateway.add(self.mock_product)

        # Assert
        self.mock_repository.add.assert_called_once_with(self.mock_product)
        assert result == self.mock_product

    def test_get_by_id(self):
        """Test that get_by_id method delegates to repository correctly."""
        # Arrange
        product_id = 1
        self.mock_repository.get_by_id.return_value = self.mock_product

        # Act
        result = self.gateway.get_by_id(product_id)

        # Assert
        self.mock_repository.get_by_id.assert_called_once_with(product_id)
        assert result == self.mock_product

    def test_get_by_name(self):
        """Test that get_by_name method delegates to repository correctly."""
        # Arrange
        product_name = "Test Product"
        self.mock_repository.get_by_name.return_value = self.mock_product

        # Act
        result = self.gateway.get_by_name(product_name)

        # Assert
        self.mock_repository.get_by_name.assert_called_once_with(product_name)
        assert result == self.mock_product

    def test_list_by_category(self):
        """Test that list_by_category method delegates to repository correctly."""
        # Arrange
        category = "test_category"
        mock_products = [self.mock_product, Mock(spec=Products)]
        self.mock_repository.list_by_category.return_value = mock_products

        # Act
        result = self.gateway.list_by_category(category)

        # Assert
        self.mock_repository.list_by_category.assert_called_once_with(category)
        assert result == mock_products
        assert len(result) == 2

    def test_list_all_products(self):
        """Test that list_all_products method delegates to repository correctly."""
        # Arrange
        mock_products = [self.mock_product, Mock(spec=Products)]
        self.mock_repository.list_all_products.return_value = mock_products

        # Act
        result = self.gateway.list_all_products()

        # Assert
        self.mock_repository.list_all_products.assert_called_once()
        assert result == mock_products
        assert len(result) == 2

    def test_update_product(self):
        """Test that update method delegates to repository correctly."""
        # Arrange
        updated_product = Mock(spec=Products)
        updated_product.id = 1
        updated_product.name = "Updated Product"
        updated_product.price = 15.99
        updated_product.category = "updated_category"

        self.mock_repository.update.return_value = updated_product

        # Act
        result = self.gateway.update(updated_product)

        # Assert
        self.mock_repository.update.assert_called_once_with(updated_product)
        assert result == updated_product
        assert result.name == "Updated Product"
        assert result.price == 15.99

    def test_delete_product(self):
        """Test that delete method delegates to repository correctly for MongoDB."""
        # Arrange
        # For MongoDB, we're likely passing the product ID directly, not a Products object
        product_id = 1
        self.mock_repository.delete.return_value = True

        # Act
        result = self.gateway.delete(product_id)

        # Assert
        self.mock_repository.delete.assert_called_once_with(product_id)
        assert result is True

    def test_get_by_ids(self):
        """Test that get_by_ids method delegates to repository correctly."""
        # Arrange - this is a method specific to MongoDB repository
        product_ids = [1, 2, 3]
        mock_products = [self.mock_product, Mock(spec=Products), Mock(spec=Products)]
        self.mock_repository.get_by_ids.return_value = mock_products

        # Act
        result = self.gateway.get_by_ids(product_ids)

        # Assert
        self.mock_repository.get_by_ids.assert_called_once_with(product_ids)
        assert result == mock_products
        assert len(result) == 3