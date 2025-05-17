# tests/unit/interfaces/presenters/test_product_presenter.py
import pytest
from unittest.mock import Mock
from tech.domain.entities.products import Products
from tech.interfaces.presenters.product_presenter import ProductPresenter


class TestProductPresenter:
    """Unit tests for the ProductPresenter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_product = Mock(spec=Products)
        self.mock_product.id = 1
        self.mock_product.name = "Test Product"
        self.mock_product.price = 10.99
        self.mock_product.category = "test_category"

        self.mock_product.created_at = "2023-01-01"
        self.mock_product.updated_at = "2023-01-02"

    def test_present_product(self):
        """Test that present_product returns the correct format with only required fields."""
        # Act
        result = ProductPresenter.present_product(self.mock_product)

        # Assert
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["name"] == "Test Product"
        assert result["price"] == 10.99
        assert result["category"] == "test_category"

        # Verify that metadata fields are excluded
        assert "created_at" not in result
        assert "updated_at" not in result

    def test_present_product_list(self):
        """Test that present_product_list formats a list of products correctly."""
        # Arrange
        mock_product2 = Mock(spec=Products)
        mock_product2.id = 2
        mock_product2.name = "Another Product"
        mock_product2.price = 20.99
        mock_product2.category = "another_category"
        mock_product2.created_at = "2023-01-03"
        mock_product2.updated_at = "2023-01-04"

        mock_products = [self.mock_product, mock_product2]

        # Act
        result = ProductPresenter.present_product_list(mock_products)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2

        # Check first product
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Test Product"
        assert result[0]["price"] == 10.99
        assert result[0]["category"] == "test_category"
        assert "created_at" not in result[0]

        # Check second product
        assert result[1]["id"] == 2
        assert result[1]["name"] == "Another Product"
        assert result[1]["price"] == 20.99
        assert result[1]["category"] == "another_category"
        assert "created_at" not in result[1]

    def test_present_empty_product_list(self):
        """Test that present_product_list handles an empty list correctly."""
        # Act
        result = ProductPresenter.present_product_list([])

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0