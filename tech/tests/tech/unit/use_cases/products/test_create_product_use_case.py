# tests/unit/use_cases/products/test_create_product_use_case.py
import pytest
from unittest.mock import Mock, patch
from tech.domain.entities.products import Products
from tech.interfaces.schemas.product_schema import ProductSchema
from tech.interfaces.repositories.product_repository import ProductRepository
from tech.use_cases.products.create_product_use_case import CreateProductUseCase


class TestCreateProductUseCase:
    """Unit tests for the CreateProductUseCase."""

    def setup_method(self):
        """Set up test dependencies."""
        self.product_repository = Mock(spec=ProductRepository)
        self.use_case = CreateProductUseCase(self.product_repository)

        # Create test data
        self.product_data = ProductSchema(
            name="Test Product",
            price=10.99,
            category="Lanche"  # Categoria válida: 'Lanche', 'Acompanhamento', 'Bebida' ou 'Sobremesa'
        )

        # Create mock product for return value
        self.mock_product = Mock(spec=Products)
        self.mock_product.id = 1
        self.mock_product.name = "Test Product"
        self.mock_product.price = 10.99
        self.mock_product.category = "Lanche"  # Categoria válida

    def test_create_product_success(self):
        """Test successful creation of a product."""
        # Arrange
        self.product_repository.get_by_name.return_value = None
        self.product_repository.add.return_value = self.mock_product

        # Act
        result = self.use_case.execute(self.product_data)

        # Assert
        self.product_repository.get_by_name.assert_called_once_with(self.product_data.name)
        self.product_repository.add.assert_called_once()

        # Verify the product passed to add has the correct attributes
        added_product = self.product_repository.add.call_args[0][0]
        assert added_product.name == self.product_data.name
        assert added_product.price == self.product_data.price
        assert added_product.category == self.product_data.category

        # Verify the result
        assert result == self.mock_product

    def test_create_product_duplicate_name(self):
        """Test creation with an existing product name raises ValueError."""
        # Arrange
        existing_product = Mock(spec=Products)
        self.product_repository.get_by_name.return_value = existing_product

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(self.product_data)

        assert "Product already exists" in str(exc_info.value)
        self.product_repository.get_by_name.assert_called_once_with(self.product_data.name)
        self.product_repository.add.assert_not_called()