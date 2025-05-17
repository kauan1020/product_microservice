# tests/unit/api/test_products_router.py
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from tech.api.products_router import router, get_product_controller
from tech.interfaces.controllers.product_controller import ProductController
from tech.interfaces.schemas.product_schema import ProductSchema

# Create a test client
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)  # Sem prefixo, usando a rota padrão
client = TestClient(app)


class TestProductsRouter:
    """Unit tests for the products router."""

    def setup_method(self):
        """Set up test dependencies."""
        self.mock_product_controller = Mock(spec=ProductController)

        mock_product = Mock()
        mock_product.dict = Mock(return_value={
            "id": 1,
            "name": "Test Product",
            "price": 10.99,
            "category": "test_category"
        })

        mock_product2 = Mock()
        mock_product2.dict = Mock(return_value={
            "id": 2,
            "name": "Another Product",
            "price": 20.99,
            "category": "other_category"
        })

        self.mock_product_controller.list_all_products.return_value = [mock_product, mock_product2]
        self.mock_product_controller.list_products_by_category.return_value = [mock_product]
        self.mock_product_controller.create_product.return_value = mock_product
        self.mock_product_controller.update_product.return_value = mock_product
        self.mock_product_controller.delete_product.return_value = {"message": "Product 1 deleted successfully"}

        self.get_controller_patch = patch(
            "tech.api.products_router.get_product_controller",
            return_value=self.mock_product_controller
        )

        self.mock_admin_required = patch(
            "tech.api.products_router.admin_required",
            return_value=True
        )

        self.get_controller_patch.start()
        self.mock_admin_required.start()

        # Sample product data
        self.product_data = {
            "name": "Test Product",
            "price": 10.99,
            "category": "test_category"
        }
        self.product_response = {
            "id": 1,
            "name": "Test Product",
            "price": 10.99,
            "category": "test_category"
        }

    def teardown_method(self):
        """Clean up after tests."""
        self.get_controller_patch.stop()
        self.mock_admin_required.stop()

    def test_get_product_controller(self):
        """Test the get_product_controller dependency function."""
        self.get_controller_patch.stop()

        with patch("tech.api.products_router.ProductRepositoryFactory") as mock_factory:
            mock_repository = Mock()
            mock_factory.create.return_value = mock_repository

            controller = get_product_controller()

            assert isinstance(controller, ProductController)
            mock_factory.create.assert_called_once()

        self.get_controller_patch.start()
