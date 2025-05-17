# tech/use_cases/products/delete_product_use_case.py
from tech.interfaces.repositories.product_repository import ProductRepository


class DeleteProductUseCase:
    """
    Caso de uso para excluir um produto.
    """

    def __init__(self, product_repository: ProductRepository):
        """
        Inicializa o caso de uso com o repositório de produtos.

        Args:
            product_repository: Repositório para interagir com os dados dos produtos.
        """
        self.product_repository = product_repository

    def execute(self, product_id: str) -> bool:
        """
        Exclui um produto pelo ID.

        Args:
            product_id: ID do produto a ser excluído.

        Returns:
            True se o produto foi excluído com sucesso, False caso contrário.

        Raises:
            ValueError: Se o produto não for encontrado.
        """
        existing_product = self.product_repository.get_by_id(product_id)
        if not existing_product:
            raise ValueError(f"Product with ID {product_id} not found")

        success = self.product_repository.delete(product_id)

        if not success:
            raise ValueError(f"Failed to delete product with ID {product_id}")

        return success