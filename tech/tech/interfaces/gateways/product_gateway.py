# tech/interfaces/gateways/product_gateway.py

from tech.domain.entities.products import Products
from tech.interfaces.repositories.product_repository import ProductRepository
from tech.infra.repositories.mongodb_product_repository import MongoDBProductRepository


class ProductGateway(ProductRepository):
    """
    Gateway that acts as an adapter between use cases and the MongoDB repository.

    This class abstracts the database operations by delegating them to the MongoDB repository,
    ensuring that the use cases do not directly interact with the database.
    """

    def __init__(self):
        """
        Initializes the ProductGateway with a MongoDB repository.
        """
        self.repository = MongoDBProductRepository()

    def add(self, product: Products) -> Products:
        """
        Adds a new product to the database.

        Args:
            product (Products): The product entity to be added.

        Returns:
            Products: The newly created product entity with an assigned ID.
        """
        return self.repository.add(product)

    def get_by_id(self, product_id: int) -> Products:
        """
        Retrieves a product by its unique ID.

        Args:
            product_id (int): The unique identifier of the product.

        Returns:
            Products: The product entity if found, otherwise None.
        """
        return self.repository.get_by_id(product_id)

    def get_by_name(self, name: str) -> Products:
        """
        Retrieves a product by its name.

        Args:
            name (str): The name of the product.

        Returns:
            Products: The product entity if found, otherwise None.
        """
        return self.repository.get_by_name(name)

    def list_by_category(self, category: str) -> list:
        """
        Retrieves a list of products filtered by category.

        Args:
            category (str): The category to filter products by.

        Returns:
            list: A list of product entities in the specified category.
        """
        return self.repository.list_by_category(category)

    def list_all_products(self) -> list:
        """
        Retrieves all available products.

        Returns:
            list: A list of all product entities.
        """
        return self.repository.list_all_products()

    def update(self, product: Products) -> Products:
        """
        Updates an existing product's details.

        Args:
            product (Products): The product entity with updated details.

        Returns:
            Products: The updated product entity.

        Raises:
            ValueError: If the product does not exist.
        """
        return self.repository.update(product)

    def delete(self, product_id) -> bool:
        """
        Deletes a product from the database.

        Args:
            product_id: The ID of the product to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        return self.repository.delete(product_id)

    def get_by_ids(self, product_ids: list) -> list:
        """
        Gets multiple products by their IDs.

        Args:
            product_ids (list): List of product IDs to retrieve.

        Returns:
            list: List of product entities found.
        """
        return self.repository.get_by_ids(product_ids)