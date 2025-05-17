import pytest
from unittest.mock import MagicMock, patch
from tech.infra.factories.product_repository_factory import ProductRepositoryFactory


@pytest.fixture(autouse=True)
def mock_mongodb_repository():
    # Mock do repositório MongoDB sem especificar spec
    mock_repo = MagicMock()

    # Configurando retornos padrão para métodos do repositório
    mock_repo.list_all_products.return_value = [
        {"id": "1", "name": "Product 1", "price": 10.99, "category": "electronics"},
        {"id": "2", "name": "Product 2", "price": 20.99, "category": "electronics"}
    ]

    mock_repo.list_products_by_category.return_value = [
        {"id": "1", "name": "Product 1", "price": 10.99, "category": "electronics"}
    ]

    mock_repo.create_product.return_value = {
        "id": "3", "name": "New Product", "price": 30.99, "category": "books"
    }

    mock_repo.update_product.return_value = {
        "id": "1", "name": "Updated Product", "price": 25.99, "category": "electronics"
    }

    mock_repo.delete_product.return_value = True

    # Aplicando o patch na factory para retornar nosso mock
    with patch.object(ProductRepositoryFactory, 'create', return_value=mock_repo):
        yield mock_repo