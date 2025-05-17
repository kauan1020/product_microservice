# from sqlalchemy.orm import Session
# from sqlalchemy import select
# from typing import List, Optional
# from tech.domain.entities.products import Products
# from tech.interfaces.repositories.product_repository import ProductRepository
# from tech.infra.repositories.sql_alchemy_models import SQLAlchemyProduct
#
#
# class SQLAlchemyProductRepository(ProductRepository):
#     """
#     Repository for managing interactions between the Products entity and the database using SQLAlchemy.
#
#     Attributes:
#         session (Session): SQLAlchemy session for database operations.
#         The session should be managed by the caller and must handle commits, rollbacks, and closing connections.
#     """
#
#     def __init__(self, session: Session):
#         self.session = session
#
#     def add(self, product: Products) -> Products:
#         """
#         Add a new product to the database.
#
#         Args:
#             product (Products): The product entity to be added to the database.
#
#         Returns:
#             Products: The newly created product with the assigned ID.
#         """
#         db_product = SQLAlchemyProduct(
#             name=product.name,
#             price=product.price,
#             category=product.category,
#         )
#         self.session.add(db_product)
#         self.session.commit()
#         self.session.refresh(db_product)
#         product.id = db_product.id
#         return product
#
#     def get_by_id(self, product_id: int) -> Optional[Products]:
#         """
#         Retrieve a product by its unique ID.
#
#         Args:
#             product_id (int): The unique identifier of the product.
#
#         Returns:
#             Optional[Products]: The product entity if found, or None if no matching product exists.
#         """
#         db_product = self.session.scalar(select(SQLAlchemyProduct).where(SQLAlchemyProduct.id == product_id))
#         if db_product:
#             return Products(
#                 id=db_product.id,
#                 name=db_product.name,
#                 price=db_product.price,
#                 category=db_product.category,
#             )
#         return None
#
#     def get_by_name(self, name: str) -> Optional[Products]:
#         """
#         Retrieve a product by its name.
#
#         Args:
#             name (str): The name of the product.
#
#         Returns:
#             Optional[Products]: The product entity if found, or None if no matching product exists.
#         """
#         db_product = self.session.scalar(select(SQLAlchemyProduct).where(SQLAlchemyProduct.name == name))
#         if db_product:
#             return Products(
#                 id=db_product.id,
#                 name=db_product.name,
#                 price=db_product.price,
#                 category=db_product.category,
#             )
#         return None
#
#     def list_by_category(self, category: str) -> List[Products]:
#         """
#         Retrieve a list of products filtered by category.
#
#         Args:
#             category (str): The category to filter products by.
#
#         Returns:
#             List[Products]: A list of products in the specified category.
#         """
#         db_products = self.session.scalars(select(SQLAlchemyProduct).where(SQLAlchemyProduct.category == category)).all()
#         return [
#             Products(
#                 id=db_product.id,
#                 name=db_product.name,
#                 price=db_product.price,
#                 category=db_product.category,
#             )
#             for db_product in db_products
#         ]
#
#     def list_all_products(self) -> List[Products]:
#         """
#         Retrieve all products from the database.
#
#         Returns:
#             List[Products]: A list of all available products.
#         """
#         db_products = self.session.scalars(select(SQLAlchemyProduct)).all()
#         return [
#             Products(
#                 id=db_product.id,
#                 name=db_product.name,
#                 price=db_product.price,
#                 category=db_product.category,
#             )
#             for db_product in db_products
#         ]
#
#     def update(self, product: Products) -> Products:
#         """
#         Update an existing product's details.
#
#         Args:
#             product (Products): The product entity with updated data.
#
#         Returns:
#             Products: The updated product entity.
#
#         Raises:
#             ValueError: If the product does not exist in the database.
#         """
#         db_product = self.session.scalar(select(SQLAlchemyProduct).where(SQLAlchemyProduct.id == product.id))
#         if not db_product:
#             raise ValueError("Product not found")
#
#         db_product.name = product.name
#         db_product.price = product.price
#         db_product.category = product.category
#         self.session.commit()
#         self.session.refresh(db_product)
#         return product
#
#     def delete(self, product: Products) -> None:
#         """
#         Delete a product from the database.
#
#         Args:
#             product (Products): The product entity to be deleted.
#
#         Returns:
#             None: This method does not return anything.
#
#         Raises:
#             ValueError: If the product does not exist in the database.
#         """
#         db_product = self.session.scalar(select(SQLAlchemyProduct).where(SQLAlchemyProduct.id == product.id))
#         if not db_product:
#             raise ValueError("Product not found")
#
#         self.session.delete(db_product)
#         self.session.commit()
