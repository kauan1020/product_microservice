# tech/use_cases/products/update_product_use_case.py
from tech.domain.entities.products import Products
from tech.interfaces.schemas.product_schema import ProductSchema
from tech.interfaces.repositories.product_repository import ProductRepository

class UpdateProductUseCase:
    """
    Caso de uso para atualizar um produto existente.
    """

    def __init__(self, product_repository: ProductRepository):
        """
        Inicializa o caso de uso com o repositório de produtos.

        Args:
            product_repository: Repositório para interagir com os dados dos produtos.
        """
        self.product_repository = product_repository

    def execute(self, product_id: str, product_data: ProductSchema) -> Products:
        """
        Atualiza um produto existente.

        Args:
            product_id: ID do produto a ser atualizado.
            product_data: Dados atualizados do produto.

        Returns:
            O produto atualizado.

        Raises:
            ValueError: Se o produto não for encontrado.
        """
        existing_product = self.product_repository.get_by_id(product_id)
        if not existing_product:
            raise ValueError(f"Product with ID {product_id} not found")

        if existing_product.name != product_data.name:
            product_with_same_name = self.product_repository.get_by_name(product_data.name)
            if product_with_same_name and product_with_same_name.id != existing_product.id:
                raise ValueError(f"Product with name '{product_data.name}' already exists")

        updated_product = Products(
            id=existing_product.id,
            name=product_data.name,
            price=product_data.price,
            category=product_data.category,
            created_at=existing_product.created_at
        )

        return self.product_repository.update(updated_product)