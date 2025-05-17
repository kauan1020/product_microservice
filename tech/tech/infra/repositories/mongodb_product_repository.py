# tech/infra/repositories/mongodb_product_repository.py
from datetime import datetime
from typing import List, Optional, Dict, Any
import random

from tech.domain.entities.products import Products
from tech.interfaces.repositories.product_repository import ProductRepository
from tech.infra.databases.mongodb import get_collection


class MongoDBProductRepository(ProductRepository):
    """
    Implementação do repositório de produtos usando MongoDB.

    Esta implementação mantém IDs inteiros para compatibilidade com o serviço de Orders.
    Em vez de usar os ObjectIDs do MongoDB como IDs primários, usamos um campo 'product_id'
    com valores inteiros.
    """

    def __init__(self):
        """
        Inicializa o repositório com a coleção de produtos.
        """
        self.collection = get_collection('products')

    def _generate_id(self) -> int:
        """
        Gera um novo ID inteiro que ainda não existe no banco de dados.

        Returns:
            int: Novo ID único
        """
        # Encontrar o maior ID atual
        result = self.collection.find_one(sort=[("product_id", -1)])

        # Se não houver produtos, começar do ID 1
        if not result or not result.get("product_id"):
            return 1

        # Caso contrário, incrementar o maior ID
        return result.get("product_id", 0) + 1

    def add(self, product: Products) -> Products:
        """
        Adiciona um novo produto ao MongoDB.

        Args:
            product: Entidade de produto a ser adicionada

        Returns:
            Products: Produto adicionado com ID atualizado
        """
        # Verificar se já existe o ID
        if product.id:
            existing_product = self.get_by_id(product.id)
            if existing_product:
                raise ValueError(f"Product with ID {product.id} already exists")

        # Gerar um novo ID inteiro se não tiver
        product_id = product.id if product.id else self._generate_id()

        # Converter a entidade para um dicionário
        product_dict = {
            "product_id": int(product_id),  # Garantir que é inteiro
            "name": product.name,
            "price": product.price,
            "category": product.category,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Inserir no MongoDB
        self.collection.insert_one(product_dict)

        # Criar uma nova instância do produto com o ID atualizado
        return Products(
            id=product_id,  # ID inteiro
            name=product.name,
            price=product.price,
            category=product.category,
            created_at=product_dict["created_at"],
            updated_at=product_dict["updated_at"]
        )

    def get_by_id(self, product_id: int) -> Optional[Products]:
        """
        Obtém um produto pelo ID.

        Args:
            product_id: ID do produto a ser obtido

        Returns:
            Optional[Products]: Produto encontrado ou None
        """
        try:
            # Converter para inteiro se for string
            if isinstance(product_id, str):
                product_id = int(product_id)

            product = self.collection.find_one({'product_id': product_id})

            if not product:
                return None

            # Mapear para a entidade Products
            return Products(
                id=product['product_id'],  # ID inteiro
                name=product['name'],
                price=product['price'],
                category=product['category'],
                created_at=product.get('created_at'),
                updated_at=product.get('updated_at')
            )
        except Exception as e:
            print(f"Erro ao obter produto por ID: {str(e)}")
            return None

    def get_by_name(self, name: str) -> Optional[Products]:
        """
        Obtém um produto pelo nome.

        Args:
            name: Nome do produto a ser obtido

        Returns:
            Optional[Products]: Produto encontrado ou None
        """
        product = self.collection.find_one({'name': name})

        if not product:
            return None

        # Mapear para a entidade Products
        return Products(
            id=product['product_id'],  # ID inteiro
            name=product['name'],
            price=product['price'],
            category=product['category'],
            created_at=product.get('created_at'),
            updated_at=product.get('updated_at')
        )

    def list_all_products(self) -> List[Products]:
        """
        Lista todos os produtos disponíveis.

        Returns:
            List[Products]: Lista de produtos
        """
        products = self.collection.find({})

        result = []
        for product in products:
            # Verificar se o documento tem um product_id válido
            if 'product_id' not in product or product['product_id'] is None:
                continue

            result.append(
                Products(
                    id=product['product_id'],  # ID inteiro
                    name=product['name'],
                    price=product['price'],
                    category=product['category'],
                    created_at=product.get('created_at'),
                    updated_at=product.get('updated_at')
                )
            )

        return result

    # Método alias para compatibilidade com a interface
    def list_all(self) -> List[Products]:
        """Alias para list_all_products"""
        return self.list_all_products()

    def list_by_category(self, category: str) -> List[Products]:
        """
        Lista produtos por categoria.

        Args:
            category: Categoria para filtrar os produtos

        Returns:
            List[Products]: Lista de produtos da categoria
        """
        products = self.collection.find({'category': category})

        result = []
        for product in products:
            # Verificar se o documento tem um product_id válido
            if 'product_id' not in product or product['product_id'] is None:
                continue

            result.append(
                Products(
                    id=product['product_id'],  # ID inteiro
                    name=product['name'],
                    price=product['price'],
                    category=product['category'],
                    created_at=product.get('created_at'),
                    updated_at=product.get('updated_at')
                )
            )

        return result

    def update(self, product: Products) -> Products:
        """
        Atualiza um produto existente.

        Args:
            product: Produto com dados atualizados

        Returns:
            Products: Produto atualizado
        """
        try:
            # Converter para inteiro se for string
            product_id = product.id
            if isinstance(product_id, str):
                product_id = int(product_id)

            # Preparar dados para atualização
            update_data = {
                "name": product.name,
                "price": product.price,
                "category": product.category,
                "updated_at": datetime.utcnow()
            }

            # Atualizar no MongoDB
            self.collection.update_one(
                {'product_id': product_id},
                {'$set': update_data}
            )

            # Obter o produto atualizado do banco
            updated_doc = self.collection.find_one({'product_id': product_id})

            # Retornar como entidade
            return Products(
                id=updated_doc['product_id'],  # ID inteiro
                name=updated_doc['name'],
                price=updated_doc['price'],
                category=updated_doc['category'],
                created_at=updated_doc.get('created_at'),
                updated_at=updated_doc.get('updated_at')
            )

        except Exception as e:
            print(f"Erro ao atualizar produto: {str(e)}")
            # Em caso de erro, retornar o produto original
            return product

    def delete(self, product_id: int) -> bool:
        """
        Remove um produto pelo ID.

        Args:
            product_id: ID do produto a remover

        Returns:
            bool: True se removido com sucesso, False caso contrário
        """
        try:
            if isinstance(product_id, str):
                product_id = int(product_id)

            result = self.collection.delete_one({'product_id': product_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Erro ao excluir produto: {str(e)}")
            return False

    def get_by_ids(self, product_ids: List[int]) -> List[Products]:
        """
        Obtém múltiplos produtos pelos seus IDs.

        Args:
            product_ids: Lista de IDs dos produtos

        Returns:
            List[Products]: Lista de produtos encontrados
        """
        int_ids = []
        for id_str in product_ids:
            try:
                int_ids.append(int(id_str))
            except Exception as e:
                print(f"ID inválido ignorado: {id_str}, erro: {str(e)}")

        if not int_ids:
            return []

        products = self.collection.find({'product_id': {'$in': int_ids}})

        result = []
        for product in products:
            if 'product_id' not in product or product['product_id'] is None:
                continue

            result.append(
                Products(
                    id=product['product_id'],
                    name=product['name'],
                    price=product['price'],
                    category=product['category'],
                    created_at=product.get('created_at'),
                    updated_at=product.get('updated_at')
                )
            )

        return result