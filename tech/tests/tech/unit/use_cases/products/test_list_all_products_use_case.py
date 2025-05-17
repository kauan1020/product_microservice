# tests/unit/use_cases/products/test_list_all_products_use_case.py
import pytest
from unittest.mock import Mock
from tech.domain.entities.products import Products
from tech.interfaces.repositories.product_repository import ProductRepository
from tech.use_cases.products.list_all_products_use_case import ListAllProductsUseCase


class TestListAllProductsUseCase:
    """Unit tests for the ListAllProductsUseCase."""

    def setup_method(self):
        """Set up test dependencies."""
        self.product_repository = Mock()
        self.product_repository.list_all_products = Mock()

        self.use_case = ListAllProductsUseCase(self.product_repository)

        self.mock_product1 = Mock(spec=Products)
        self.mock_product1.id = 1
        self.mock_product1.name = "Product 1"
        self.mock_product1.category = "Lanche"  # Categoria válida

        self.mock_product2 = Mock(spec=Products)
        self.mock_product2.id = 2
        self.mock_product2.name = "Product 2"
        self.mock_product2.category = "Bebida"  # Categoria válida

    def test_list_all_products_with_results(self):
        """Test listing all products with results."""
        # Arrange
        mock_products = [self.mock_product1, self.mock_product2]
        self.product_repository.list_all_products.return_value = mock_products

        # Act
        result = self.use_case.execute()

        # Assert
        self.product_repository.list_all_products.assert_called_once()
        assert result == mock_products
        assert len(result) == 2

    def test_list_all_products_empty(self):
        """Test listing all products with no results."""
        # Arrange
        self.product_repository.list_all_products.return_value = []

        # Act
        result = self.use_case.execute()

        # Assert
        self.product_repository.list_all_products.assert_called_once()
        assert result == []
        assert len(result) == 0