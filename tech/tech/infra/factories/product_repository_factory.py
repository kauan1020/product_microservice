import os
from tech.interfaces.repositories.product_repository import ProductRepository
from tech.infra.repositories.mongodb_product_repository import MongoDBProductRepository


class ProductRepositoryFactory:
    """
    Factory para criar instâncias do repositório de produtos.

    Esta factory permite alternar facilmente entre diferentes implementações
    do repositório (MongoDB, SQLAlchemy, etc.) com base em configurações de ambiente.
    """

    @staticmethod
    def create() -> ProductRepository:
        """
        Cria e retorna uma instância do repositório de produtos.

        Returns:
            ProductRepository: Implementação concreta do repositório de produtos
        """
        return MongoDBProductRepository()