import pytest
from unittest.mock import Mock
from tech.domain.entities.products import Products
from tech.interfaces.repositories.product_repository import ProductRepository
from tech.use_cases.products.get_product_use_case import GetProductUseCase


class TestGetProductUseCase:
    """Unit tests for the GetProductUseCase."""

    def setup_method(self):
        """Set up test dependencies."""
        self.product_repository = Mock(spec=ProductRepository)
        self.use_case = GetProductUseCase(self.product_repository)

        # Create mock product
        self.mock_product = Mock(spec=Products)
        self.mock_product.id = 1
        self.mock_product.name = "Test Product"
        self.product_id = 1

    def test_get_product_success(self):
        """Test successful retrieval of a product."""
        # Arrange
        self.product_repository.get_by_id.return_value = self.mock_product

        # Act
        result = self.use_case.execute(self.product_id)

        # Assert
        self.product_repository.get_by_id.assert_called_once_with(self.product_id)
        assert result == self.mock_product

    def test_get_product_not_found(self):
        """Test retrieval of non-existent product raises ValueError."""
        # Arrange
        self.product_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(999)

        assert "Product not found" in str(exc_info.value)
        self.product_repository.get_by_id.assert_called_once_with(999)
