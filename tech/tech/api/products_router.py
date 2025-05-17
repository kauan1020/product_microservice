# tech/api/products_router.py
from fastapi import APIRouter, Depends, HTTPException
from tech.infra.factories.product_repository_factory import ProductRepositoryFactory
from tech.interfaces.schemas.product_schema import ProductSchema
from tech.use_cases.products.create_product_use_case import CreateProductUseCase
from tech.use_cases.products.list_products_by_category_use_case import ListProductsByCategoryUseCase
from tech.use_cases.products.list_all_products_use_case import ListAllProductsUseCase
from tech.use_cases.products.update_product_use_case import UpdateProductUseCase
from tech.use_cases.products.delete_product_use_case import DeleteProductUseCase
from tech.interfaces.controllers.product_controller import ProductController
from tech.interfaces.middlewares.admin_auth_middleware import admin_required

router = APIRouter()


def get_product_controller() -> ProductController:
    """
    Dependency injection for the ProductController.

    This function initializes the controller by injecting the necessary use cases
    and the ProductGateway, ensuring proper separation of concerns.

    Returns:
        ProductController: Instance of ProductController with required dependencies.
    """
    # Usando a factory para criar o repositório
    product_repository = ProductRepositoryFactory.create()

    return ProductController(
        create_product_use_case=CreateProductUseCase(product_repository),
        list_products_by_category_use_case=ListProductsByCategoryUseCase(product_repository),
        list_all_products_use_case=ListAllProductsUseCase(product_repository),
        update_product_use_case=UpdateProductUseCase(product_repository),
        delete_product_use_case=DeleteProductUseCase(product_repository),
    )


@router.get('/')
def list_all_products(
        controller: ProductController = Depends(get_product_controller)
) -> list:
    """
    Retrieves all available products.

    Args:
        controller (ProductController): The ProductController instance.

    Returns:
        list: A list of formatted product details.

    Raises:
        HTTPException: If no products are found.
    """
    return controller.list_all_products()


@router.get('/{category}')
def list_products_by_category(
        category: str,
        controller: ProductController = Depends(get_product_controller)
) -> list:
    """
    Retrieves a list of products filtered by category.

    Args:
        category (str): The category to filter products by.
        controller (ProductController): The ProductController instance.

    Returns:
        list: A list of formatted product details.

    Raises:
        HTTPException: If no products are found in the specified category.
    """
    return controller.list_products_by_category(category)


# Admin-only routes - protected with admin authentication
@router.post('/', status_code=201)
def create_product(
        product: ProductSchema,
        controller: ProductController = Depends(get_product_controller),
        _: bool = Depends(admin_required)
) -> dict:
    """
    Creates a new product. Admin access only.

    Args:
        product (ProductSchema): The product details to be created.
        controller (ProductController): The ProductController instance.

    Returns:
        dict: The formatted response containing product details.
    """
    return controller.create_product(product)


@router.put('/{product_id}')
def update_product(
        product_id: str,
        product: ProductSchema,
        controller: ProductController = Depends(get_product_controller),
        _: bool = Depends(admin_required)
) -> dict:
    """
    Updates a product by its ID. Admin access only.

    Args:
        product_id (str): The ID of the product to update.
        product (ProductSchema): The updated product details.
        controller (ProductController): The ProductController instance.

    Returns:
        dict: The formatted response containing the updated product details.

    Raises:
        HTTPException: If the product is not found.
    """
    return controller.update_product(product_id, product)


@router.delete('/{product_id}')
def delete_product(
        product_id: str,
        controller: ProductController = Depends(get_product_controller),
        _: bool = Depends(admin_required)
) -> dict:
    """
    Deletes a product by its ID. Admin access only.

    Args:
        product_id (str): The ID of the product to delete.
        controller (ProductController): The ProductController instance.

    Returns:
        dict: A success message confirming deletion.

    Raises:
        HTTPException: If the product is not found.
    """
    return controller.delete_product(product_id)

