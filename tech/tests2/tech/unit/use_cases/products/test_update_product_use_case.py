# tests/unit/use_cases/products/test_update_product_use_case.py
import pytest
from unittest.mock import Mock
from tech.domain.entities.products import Products
from tech.interfaces.schemas.product_schema import ProductSchema
from tech.interfaces.repositories.product_repository import ProductRepository
from tech.use_cases.products.update_product_use_case import UpdateProductUseCase


class TestUpdateProductUseCase:
    """Unit tests for the UpdateProductUseCase."""

    def setup_method(self):
        """Set up test dependencies."""
        self.product_repository = Mock(spec=ProductRepository)
        self.use_case = UpdateProductUseCase(self.product_repository)

        # Create existing product
        self.existing_product = Mock(spec=Products)
        self.existing_product.id = 1
        self.existing_product.name = "Existing Product"
        self.existing_product.price = 10.99
        self.existing_product.category = "Lanche"  # Categoria válida
        self.existing_product.created_at = "2023-01-01"

        # Create updated product data
        self.product_data = ProductSchema(
            name="Updated Product",
            price=15.99,
            category="Bebida"  # Categoria válida: 'Lanche', 'Acompanhamento', 'Bebida' ou 'Sobremesa'
        )

        # Create updated product
        self.updated_product = Mock(spec=Products)
        self.updated_product.id = 1
        self.updated_product.name = "Updated Product"
        self.updated_product.price = 15.99
        self.updated_product.category = "Bebida"  # Categoria válida

    def test_update_product_success(self):
        """Test successful update of a product."""
        # Arrange
        product_id = "1"
        self.product_repository.get_by_id.return_value = self.existing_product
        self.product_repository.get_by_name.return_value = None  # No duplicate name
        self.product_repository.update.return_value = self.updated_product

        # Act
        result = self.use_case.execute(product_id, self.product_data)

        # Assert
        self.product_repository.get_by_id.assert_called_once_with(product_id)
        self.product_repository.get_by_name.assert_called_once_with(self.product_data.name)
        self.product_repository.update.assert_called_once()

        # Verify the product passed to update has the correct attributes
        updated_product = self.product_repository.update.call_args[0][0]
        assert updated_product.id == int(product_id)
        assert updated_product.name == self.product_data.name
        assert updated_product.price == self.product_data.price
        assert updated_product.category == self.product_data.category
        assert updated_product.created_at == self.existing_product.created_at

        # Verify the result
        assert result == self.updated_product

    def test_update_product_not_found(self):
        """Test update of non-existent product raises ValueError."""
        # Arrange
        product_id = "999"
        self.product_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(product_id, self.product_data)

        assert f"Product with ID {product_id} not found" in str(exc_info.value)
        self.product_repository.get_by_id.assert_called_once_with(product_id)
        self.product_repository.get_by_name.assert_not_called()
        self.product_repository.update.assert_not_called()

    def test_update_product_duplicate_name(self):
        """Test update with a duplicate name raises ValueError."""
        # Arrange
        product_id = "1"
        duplicate_product = Mock(spec=Products)
        duplicate_product.id = 2  # Different ID from the one being updated
        duplicate_product.name = "Updated Product"

        self.product_repository.get_by_id.return_value = self.existing_product
        self.product_repository.get_by_name.return_value = duplicate_product

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(product_id, self.product_data)

        assert f"Product with name '{self.product_data.name}' already exists" in str(exc_info.value)
        self.product_repository.get_by_id.assert_called_once_with(product_id)
        self.product_repository.get_by_name.assert_called_once_with(self.product_data.name)
        self.product_repository.update.assert_not_called()

    def test_update_product_same_name(self):
        """Test update with the same name passes through."""
        # Arrange
        product_id = "1"

        # The product with the same name is the same product (same ID)
        self.product_repository.get_by_id.return_value = self.existing_product
        self.product_repository.get_by_name.return_value = self.existing_product
        self.product_repository.update.return_value = self.updated_product

        # Act
        result = self.use_case.execute(product_id, self.product_data)

        # Assert
        self.product_repository.get_by_id.assert_called_once_with(product_id)
        self.product_repository.get_by_name.assert_called_once_with(self.product_data.name)
        self.product_repository.update.assert_called_once()
        assert result == self.updated_product