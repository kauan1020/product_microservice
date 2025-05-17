import pytest
from unittest.mock import Mock
from tech.domain.entities.products import Products
from tech.interfaces.repositories.product_repository import ProductRepository
from tech.use_cases.products.delete_product_use_case import DeleteProductUseCase


class TestDeleteProductUseCase:
    """Unit tests for the DeleteProductUseCase."""

    def setup_method(self):
        """Set up test dependencies."""
        self.product_repository = Mock(spec=ProductRepository)
        self.use_case = DeleteProductUseCase(self.product_repository)

        # Create mock product
        self.mock_product = Mock(spec=Products)
        self.mock_product.id = 1
        self.product_id = "1"

    def test_delete_product_success(self):
        """Test successful deletion of a product."""
        # Arrange
        self.product_repository.get_by_id.return_value = self.mock_product
        self.product_repository.delete.return_value = True

        # Act
        result = self.use_case.execute(self.product_id)

        # Assert
        self.product_repository.get_by_id.assert_called_once_with(self.product_id)
        self.product_repository.delete.assert_called_once_with(self.product_id)
        assert result is True

    def test_delete_product_not_found(self):
        """Test deletion of non-existent product raises ValueError."""
        # Arrange
        self.product_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute("999")

        assert "Product with ID 999 not found" in str(exc_info.value)
        self.product_repository.get_by_id.assert_called_once_with("999")
        self.product_repository.delete.assert_not_called()

    def test_delete_product_failure(self):
        """Test deletion failure raises ValueError."""
        # Arrange
        self.product_repository.get_by_id.return_value = self.mock_product
        self.product_repository.delete.return_value = False

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.execute(self.product_id)

        assert f"Failed to delete product with ID {self.product_id}" in str(exc_info.value)
        self.product_repository.get_by_id.assert_called_once_with(self.product_id)
        self.product_repository.delete.assert_called_once_with(self.product_id)
