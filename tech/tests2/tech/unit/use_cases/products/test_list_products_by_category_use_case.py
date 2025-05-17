import pytest
from unittest.mock import Mock
from tech.domain.entities.products import Products
from tech.interfaces.repositories.product_repository import ProductRepository
from tech.use_cases.products.list_products_by_category_use_case import ListProductsByCategoryUseCase


class TestListProductsByCategoryUseCase:
    """Unit tests for the ListProductsByCategoryUseCase."""

    def setup_method(self):
        """Set up test dependencies."""
        self.product_repository = Mock(spec=ProductRepository)
        self.use_case = ListProductsByCategoryUseCase(self.product_repository)

        # Create mock products
        self.mock_product1 = Mock(spec=Products)
        self.mock_product1.id = 1
        self.mock_product1.name = "Product 1"
        self.mock_product1.category = "category1"

        self.mock_product2 = Mock(spec=Products)
        self.mock_product2.id = 2
        self.mock_product2.name = "Product 2"
        self.mock_product2.category = "category1"

    def test_list_products_by_category_with_results(self):
        """Test listing products by category with results."""
        # Arrange
        category = "category1"
        mock_products = [self.mock_product1, self.mock_product2]
        self.product_repository.list_by_category.return_value = mock_products

        # Act
        result = self.use_case.execute(category)

        # Assert
        self.product_repository.list_by_category.assert_called_once_with(category)
        assert result == mock_products
        assert len(result) == 2

    def test_list_products_by_category_empty(self):
        """Test listing products by category with no results."""
        # Arrange
        category = "nonexistent_category"
        self.product_repository.list_by_category.return_value = []

        # Act
        result = self.use_case.execute(category)

        # Assert
        self.product_repository.list_by_category.assert_called_once_with(category)
        assert result == []
        assert len(result) == 0