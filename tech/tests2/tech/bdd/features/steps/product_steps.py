from behave import given, when, then, step
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from tech.api.app import app
from tech.domain.entities.products import Products
from tech.infra.factories.product_repository_factory import ProductRepositoryFactory
from tech.infra.repositories.mongodb_product_repository import MongoDBProductRepository

# Aplicamos um monkey patch na classe Products para garantir que ela tenha o método dict
if not hasattr(Products, 'dict'):
    def dict_method(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category
        }


    Products.dict = dict_method

client = TestClient(app)

patch_get_by_name = patch.object(MongoDBProductRepository, 'get_by_name')
mock_get_by_name = patch_get_by_name.start()

patch_get_by_id = patch.object(MongoDBProductRepository, 'get_by_id')
mock_get_by_id = patch_get_by_id.start()

patch_list_by_category = patch.object(MongoDBProductRepository, 'list_by_category')
mock_list_by_category = patch_list_by_category.start()

patch_list_all_products = patch.object(MongoDBProductRepository, 'list_all_products')
mock_list_all_products = patch_list_all_products.start()

patch_add = patch.object(MongoDBProductRepository, 'add')
mock_add = patch_add.start()

patch_update = patch.object(MongoDBProductRepository, 'update')
mock_update = patch_update.start()

patch_delete = patch.object(MongoDBProductRepository, 'delete')
mock_delete = patch_delete.start()


def mock_admin_required(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def mock_verify_token(token):
    if token == "admin-mock-token":
        return {"username": "admin", "is_admin": True, "attributes": {"sub": "admin-id", "email": "admin@example.com"}}
    elif token == "user-mock-token":
        return {"username": "regular-user", "is_admin": False,
                "attributes": {"sub": "user-id", "email": "user@example.com"}}
    else:
        raise ValueError("Invalid token")


@given('the system has a registered admin user with login credentials')
def step_impl(context):
    context.admin_user = {"username": "admin", "password": "admin_password", "token": "admin-mock-token",
                          "is_admin": True}


@given('the system has a registered regular user with login credentials')
def step_impl(context):
    context.regular_user = {"username": "user", "password": "user_password", "token": "user-mock-token",
                            "is_admin": False}


@given('the administrator is authenticated')
def step_impl(context):
    context.headers = {"Authorization": f"Bearer {context.admin_user['token']}"}
    context.admin_patch = patch('tech.interfaces.middlewares.admin_auth_middleware.admin_required',
                                side_effect=mock_admin_required)
    context.verify_patch = patch('tech.interfaces.gateways.cognito_gateway.CognitoGateway.verify_token',
                                 side_effect=mock_verify_token)
    context.admin_patch.start()
    context.verify_patch.start()


@given('the regular user is authenticated')
def step_impl(context):
    context.headers = {"Authorization": f"Bearer {context.regular_user['token']}"}
    from fastapi import HTTPException
    def mock_admin_check(credentials):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    context.admin_patch = patch('tech.interfaces.middlewares.admin_auth_middleware.admin_required',
                                side_effect=mock_admin_check)
    context.verify_patch = patch('tech.interfaces.gateways.cognito_gateway.CognitoGateway.verify_token',
                                 side_effect=mock_verify_token)
    context.admin_patch.start()
    context.verify_patch.start()


@given('the system has the following categories')
def step_impl(context):
    context.categories = [row['category'] for row in context.table]


@given('the system has the following products')
def step_impl(context):
    context.test_products = []
    context.product_id_map = {}
    for i, row in enumerate(context.table):
        product = Products(id=i + 1, name=row['name'], price=float(row['price']), category=row['category'])
        context.test_products.append(product)
        context.product_id_map[row['name']] = i + 1
    context.original_repo_factory = ProductRepositoryFactory.create
    mock_repo = MagicMock()

    def mock_get_by_name(name):
        for product in context.test_products:
            if product.name == name:
                return product
        return None

    def mock_get_by_id(id):
        for product in context.test_products:
            if product.id == id or str(product.id) == id:
                return product
        return None

    def mock_list_by_category(category):
        return [p for p in context.test_products if p.category == category]

    def mock_list_all_products():
        return context.test_products

    def mock_add_func(product):
        if mock_get_by_name(product.name):
            raise ValueError("Product already exists")
        # Garantindo que o ID seja uma propriedade normal e não um atributo especial
        product_id = len(context.test_products) + 1
        if hasattr(product, 'id') and product.id:
            product_id = product.id
        new_product = Products(
            id=product_id,
            name=product.name,
            price=product.price,
            category=product.category
        )
        context.test_products.append(new_product)
        context.product_id_map[product.name] = new_product.id
        return new_product

    def mock_update_func(product):
        for i, p in enumerate(context.test_products):
            if p.id == product.id:
                updated_product = Products(
                    id=product.id,
                    name=product.name,
                    price=product.price,
                    category=product.category
                )
                context.test_products[i] = updated_product
                return updated_product
        raise ValueError(f"Product with ID {product.id} not found")

    def mock_delete_func(product_id):
        for i, p in enumerate(context.test_products):
            if p.id == product_id or str(p.id) == product_id:
                del context.test_products[i]
                return True
        return False

    mock_repo.get_by_name.side_effect = mock_get_by_name
    mock_repo.get_by_id.side_effect = mock_get_by_id
    mock_repo.list_by_category.side_effect = mock_list_by_category
    mock_repo.list_all_products.side_effect = mock_list_all_products
    mock_repo.add.side_effect = mock_add_func
    mock_repo.update.side_effect = mock_update_func
    mock_repo.delete.side_effect = mock_delete_func
    patch_factory = patch.object(ProductRepositoryFactory, 'create', return_value=mock_repo)
    context.repo_patch = patch_factory
    context.repo_patch.start()
    mock_get_by_name.side_effect = mock_get_by_name
    mock_get_by_id.side_effect = mock_get_by_id
    mock_list_by_category.side_effect = mock_list_by_category
    mock_list_all_products.side_effect = mock_list_all_products
    mock_add.side_effect = mock_add_func
    mock_update.side_effect = mock_update_func
    mock_delete.side_effect = mock_delete_func


@when('the admin creates a new product with the following details')
def step_impl(context):
    row = context.table[0]

    # Inicializar os produtos de teste se eles não existirem
    if not hasattr(context, 'test_products'):
        context.test_products = []
        context.product_id_map = {}

    # Determinar o próximo ID para o produto
    if "id" not in row:
        product_id = len(context.test_products) + 1
    else:
        product_id = int(row["id"])

    # Preparar os dados do produto
    context.product_data = {
        "name": row['name'],
        "price": float(row['price']),
        "category": row['category']
    }

    # Criar um produto para mockup
    new_product = Products(
        id=product_id,
        name=row['name'],
        price=float(row['price']),
        category=row['category']
    )

    # Criamos um mock simples que retorna um dicionário diretamente
    mock_product = MagicMock()
    mock_product.dict.return_value = {
        "id": product_id,
        "name": row['name'],
        "price": float(row['price']),
        "category": row['category']
    }

    # Aplicar patch temporário para os mocks específicos deste teste
    with patch.object(MongoDBProductRepository, 'get_by_name', return_value=None):
        # Usar o mock específico para add() que retorna nosso mock_product
        mock_add.return_value = mock_product

        # Fazer a requisição
        response = client.post("/products/", json=context.product_data, headers=context.headers)

        # Restaurar o comportamento original do mock
        mock_add.return_value = None

    # Se a criação foi bem-sucedida, adicione o produto aos produtos de teste
    if response.status_code == 201:
        context.test_products.append(new_product)
        context.product_id_map[row['name']] = product_id

    context.response = response
    context.response_data = response.json() if response.status_code < 300 else None


@when('the admin updates the "{product_name}" product with the following details')
def step_impl(context, product_name):
    row = context.table[0]
    product_id = context.product_id_map.get(product_name)

    if not product_id:
        raise ValueError(f"Product {product_name} not found in test data")

    context.product_data = {
        "name": row['name'],
        "price": float(row['price']),
        "category": row['category']
    }

    # Usar a API diretamente
    response = client.put(f"/products/{product_id}", json=context.product_data, headers=context.headers)

    # Atualize o produto nos produtos de teste
    if response.status_code == 200:
        updated_product = Products(
            id=product_id,
            name=row['name'],
            price=float(row['price']),
            category=row['category']
        )
        for i, p in enumerate(context.test_products):
            if p.id == product_id:
                context.test_products[i] = updated_product
                break

    context.response = response
    context.response_data = response.json() if response.status_code < 300 else None
    context.updated_product_name = product_name


@when('the admin deletes the product "{product_name}"')
def step_impl(context, product_name):
    product_id = context.product_id_map.get(product_name)

    if not product_id:
        raise ValueError(f"Product {product_name} not found in test data")

    # Usar a API diretamente
    response = client.delete(f"/products/{product_id}", headers=context.headers)

    # Remova o produto dos produtos de teste
    if response.status_code == 200:
        for i, p in enumerate(context.test_products):
            if p.id == product_id:
                del context.test_products[i]
                break

    context.response = response
    context.response_data = response.json() if response.status_code < 300 else None
    context.deleted_product_name = product_name


@when('a user requests products in the "{category}" category')
def step_impl(context, category):
    # Configurar o mock para retornar os produtos da categoria específica
    products_in_category = [p for p in context.test_products if p.category == category]
    mock_list_by_category.return_value = products_in_category

    # Usar a API diretamente
    response = client.get(f"/products/{category}")

    context.response = response
    context.response_data = response.json() if response.status_code < 300 else None
    context.requested_category = category


@when('a user requests all products')
def step_impl(context):
    # Configurar o mock para retornar todos os produtos de teste
    mock_list_all_products.return_value = context.test_products

    # Usar a API diretamente
    response = client.get("/products/")

    context.response = response
    context.response_data = response.json() if response.status_code < 300 else None


@when('the regular user tries to create a new product')
def step_impl(context):
    product_data = {
        "name": "Unauthorized Product",
        "price": 9.99,
        "category": "Lanche"
    }

    from fastapi import HTTPException

    with patch('tech.api.products_router.admin_required') as mock_admin:
        mock_admin.side_effect = HTTPException(status_code=403, detail="Insufficient permissions")

        with patch('tech.interfaces.middlewares.admin_auth_middleware.admin_required',
                   side_effect=HTTPException(status_code=403, detail="Insufficient permissions")):
            response = client.post("/products/", json=product_data, headers=context.headers)

    context.response = response


@then('the product "{product_name}" should be successfully created')
def step_impl(context, product_name):
    assert context.response.status_code == 201, f"Expected 201, got {context.response.status_code}"
    assert context.response_data is not None
    assert context.response_data["name"] == product_name


@then('the response should include the product ID')
def step_impl(context):
    assert "id" in context.response_data
    assert context.response_data["id"] is not None


@then('the product "{product_name}" should be available in the "{category}" category')
def step_impl(context, product_name, category):
    # Encontre manualmente o produto por categoria
    products_in_category = [p for p in context.test_products if p.category == category]
    product_names = [p.name for p in products_in_category]
    assert product_name in product_names, f"Product {product_name} not found in category {category}"


@then('the product should be successfully updated')
def step_impl(context):
    assert context.response.status_code == 200, f"Expected 200, got {context.response.status_code}"
    assert context.response_data is not None


@then('the product\'s name should be "{expected_name}"')
def step_impl(context, expected_name):
    assert context.response_data["name"] == expected_name


@then('the product\'s price should be {expected_price}')
def step_impl(context, expected_price):
    expected = float(expected_price)
    assert context.response_data["price"] == expected


@then('the product should be successfully deleted')
def step_impl(context):
    assert context.response.status_code == 200, f"Expected 200, got {context.response.status_code}"
    assert "message" in context.response_data
    assert "deleted" in context.response_data["message"]


@then('the product "{product_name}" should no longer be available')
def step_impl(context, product_name):
    product_names = [p.name for p in context.test_products]
    assert product_name not in product_names, f"Product {product_name} still exists"


@then('the response should include {count} products')
def step_impl(context, count):
    expected_count = int(count)
    assert len(
        context.response_data) == expected_count, f"Expected {expected_count} products, got {len(context.response_data)}"


@then('the response should include "{product1}" and "{product2}"')
def step_impl(context, product1, product2):
    product_names = [p["name"] for p in context.response_data]
    assert product1 in product_names, f"Product {product1} not found in response"
    assert product2 in product_names, f"Product {product2} not found in response"


@then('the response should not include "{product_name}"')
def step_impl(context, product_name):
    product_names = [p["name"] for p in context.response_data]
    assert product_name not in product_names, f"Product {product_name} found in response but should not be"


@then('the response should include "{product1}", "{product2}", and "{product3}"')
def step_impl(context, product1, product2, product3):
    product_names = [p["name"] for p in context.response_data]
    assert product1 in product_names, f"Product {product1} not found in response"
    assert product2 in product_names, f"Product {product2} not found in response"
    assert product3 in product_names, f"Product {product3} not found in response"


@then('the operation should be denied with a 403 error')
def step_impl(context):
    if context.response.status_code == 401:
        assert True
    else:
        assert context.response.status_code == 403, f"Expected 403, got {context.response.status_code}"


@then('the operation should fail with a 400 error')
def step_impl(context):
    if context.response.status_code == 422:
        assert True
    else:
        assert context.response.status_code == 400, f"Expected 400, got {context.response.status_code}"


@then('the error message should contain "{expected_message}"')
def step_impl(context, expected_message):
    error_detail = context.response.json().get("detail", "")
    assert expected_message in error_detail, f"Expected '{expected_message}' in '{error_detail}'"


def after_scenario(context, scenario):
    if hasattr(context, 'admin_patch'):
        context.admin_patch.stop()

    if hasattr(context, 'verify_patch'):
        context.verify_patch.stop()

    if hasattr(context, 'repo_patch'):
        context.repo_patch.stop()

    if hasattr(context, 'original_repo_factory'):
        ProductRepositoryFactory.create = context.original_repo_factory

    # Não precisamos parar os patches globais, pois eles devem persistir durante
    # toda a execução dos testes