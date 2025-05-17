# tests/unit/interfaces/controllers/test_product_controller.py
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from tech.interfaces.controllers.product_controller import ProductController
from tech.use_cases.products.create_product_use_case import CreateProductUseCase
from tech.use_cases.products.list_products_by_category_use_case import ListProductsByCategoryUseCase
from tech.use_cases.products.list_all_products_use_case import ListAllProductsUseCase
from tech.use_cases.products.update_product_use_case import UpdateProductUseCase
from tech.use_cases.products.delete_product_use_case import DeleteProductUseCase
from tech.interfaces.schemas.product_schema import ProductSchema
from tech.domain.entities.products import Products


class TestProductController:
    def setup_method(self):
        # Criar mocks para os use cases
        self.create_product_use_case = Mock(spec=CreateProductUseCase)
        self.list_products_by_category_use_case = Mock(spec=ListProductsByCategoryUseCase)
        self.list_all_products_use_case = Mock(spec=ListAllProductsUseCase)
        self.update_product_use_case = Mock(spec=UpdateProductUseCase)
        self.delete_product_use_case = Mock(spec=DeleteProductUseCase)

        # Inicializar o controller com os mocks
        self.controller = ProductController(
            self.create_product_use_case,
            self.list_products_by_category_use_case,
            self.list_all_products_use_case,
            self.update_product_use_case,
            self.delete_product_use_case
        )

        # Mock de produtos para testes
        self.mock_product = Mock(spec=Products)
        self.mock_product.id = 1
        self.mock_product.name = "Test Product"
        self.mock_product.price = 10.99
        self.mock_product.category = "Lanche"  # Categoria válida

        # Configurar o método dict() no mock do produto
        self.mock_product.dict.return_value = {
            "id": 1,
            "name": "Test Product",
            "price": 10.99,
            "category": "Lanche"
        }

        # Mock de schema de produto para testes - usando categoria válida
        self.product_data = ProductSchema(
            name="Test Product",
            price=10.99,
            category="Lanche"  # Categoria válida: 'Lanche', 'Acompanhamento', 'Bebida' ou 'Sobremesa'
        )

    def test_create_product_success(self):
        # Arrange
        self.create_product_use_case.execute.return_value = self.mock_product
        expected_response = self.mock_product.dict()

        # Act
        result = self.controller.create_product(self.product_data)

        # Assert
        self.create_product_use_case.execute.assert_called_once_with(self.product_data)
        assert result == expected_response

    def test_create_product_error(self):
        # Arrange
        error_message = "Product already exists"
        self.create_product_use_case.execute.side_effect = ValueError(error_message)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.controller.create_product(self.product_data)

        # Verify
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == error_message
        self.create_product_use_case.execute.assert_called_once_with(self.product_data)

    def test_list_products_by_category_success(self):
        # Arrange
        category = "Lanche"  # Categoria válida
        mock_products = [self.mock_product, Mock(spec=Products)]
        mock_products[1].dict.return_value = {
            "id": 2,
            "name": "Another Product",
            "price": 20.99,
            "category": "Lanche"
        }

        self.list_products_by_category_use_case.execute.return_value = mock_products
        expected_response = [product.dict() for product in mock_products]

        # Act
        result = self.controller.list_products_by_category(category)

        # Assert
        self.list_products_by_category_use_case.execute.assert_called_once_with(category)
        assert result == expected_response

    def test_list_products_by_category_empty(self):
        # Arrange
        category = "Bebida"  # Categoria válida
        self.list_products_by_category_use_case.execute.return_value = []

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.controller.list_products_by_category(category)

        # Verify
        assert exc_info.value.status_code == 404
        assert f"No products found in category: {category}" in exc_info.value.detail
        self.list_products_by_category_use_case.execute.assert_called_once_with(category)

    def test_list_all_products_success(self):
        # Arrange
        mock_products = [self.mock_product, Mock(spec=Products)]
        mock_products[1].dict.return_value = {
            "id": 2,
            "name": "Another Product",
            "price": 20.99,
            "category": "Bebida"  # Outra categoria válida
        }

        self.list_all_products_use_case.execute.return_value = mock_products
        expected_response = [product.dict() for product in mock_products]

        # Act
        result = self.controller.list_all_products()

        # Assert
        self.list_all_products_use_case.execute.assert_called_once()
        assert result == expected_response

    def test_list_all_products_empty(self):
        # Arrange
        self.list_all_products_use_case.execute.return_value = []

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.controller.list_all_products()

        # Verify
        assert exc_info.value.status_code == 404
        assert "No products found" in exc_info.value.detail
        self.list_all_products_use_case.execute.assert_called_once()

    def test_update_product_success(self):
        # Arrange
        updated_mock_product = Mock(spec=Products)
        updated_mock_product.dict.return_value = {
            "id": 1,
            "name": "Updated Product",
            "price": 15.99,
            "category": "Acompanhamento"  # Categoria válida
        }

        self.update_product_use_case.execute.return_value = updated_mock_product
        expected_response = updated_mock_product.dict()

        # Act
        result = self.controller.update_product("1", self.product_data)

        # Assert
        self.update_product_use_case.execute.assert_called_once_with("1", self.product_data)
        assert result == expected_response

    def test_update_product_not_found(self):
        # Arrange
        error_message = "Product with ID 999 not found"
        self.update_product_use_case.execute.side_effect = ValueError(error_message)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.controller.update_product("999", self.product_data)

        # Verify
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == error_message
        self.update_product_use_case.execute.assert_called_once_with("999", self.product_data)

    def test_delete_product_success(self):
        # Arrange
        self.delete_product_use_case.execute.return_value = True
        expected_response = {"message": "Product 1 deleted successfully"}

        # Act
        result = self.controller.delete_product("1")

        # Assert
        self.delete_product_use_case.execute.assert_called_once_with("1")
        assert result == expected_response

    def test_delete_product_not_found(self):
        # Arrange
        error_message = "Product with ID 999 not found"
        self.delete_product_use_case.execute.side_effect = ValueError(error_message)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.controller.delete_product("999")

        # Verify
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == error_message
        self.delete_product_use_case.execute.assert_called_once_with("999")

    def test_delete_product_failure(self):
        # Arrange
        error_message = "Failed to delete product with ID 1"
        self.delete_product_use_case.execute.side_effect = ValueError(error_message)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.controller.delete_product("1")

        # Verify
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == error_message
        self.delete_product_use_case.execute.assert_called_once_with("1")