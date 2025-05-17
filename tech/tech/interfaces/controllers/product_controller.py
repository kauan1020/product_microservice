# tech/interfaces/controllers/product_controller.py
from fastapi import HTTPException
from typing import List, Dict, Any

from tech.use_cases.products.create_product_use_case import CreateProductUseCase
from tech.use_cases.products.list_products_by_category_use_case import ListProductsByCategoryUseCase
from tech.use_cases.products.list_all_products_use_case import ListAllProductsUseCase
from tech.use_cases.products.update_product_use_case import UpdateProductUseCase
from tech.use_cases.products.delete_product_use_case import DeleteProductUseCase
from tech.interfaces.schemas.product_schema import ProductSchema

class ProductController:
    """
    Controlador responsável por gerenciar operações relacionadas a produtos.
    """

    def __init__(
            self,
            create_product_use_case: CreateProductUseCase,
            list_products_by_category_use_case: ListProductsByCategoryUseCase,
            list_all_products_use_case: ListAllProductsUseCase,
            update_product_use_case: UpdateProductUseCase,
            delete_product_use_case: DeleteProductUseCase
    ):
        self.create_product_use_case = create_product_use_case
        self.list_products_by_category_use_case = list_products_by_category_use_case
        self.list_all_products_use_case = list_all_products_use_case
        self.update_product_use_case = update_product_use_case
        self.delete_product_use_case = delete_product_use_case

    def create_product(self, product_data: ProductSchema) -> Dict[str, Any]:
        """
        Cria um novo produto e retorna uma resposta formatada.

        Args:
            product_data: Os dados necessários para criar um novo produto.

        Returns:
            Uma resposta formatada contendo os detalhes do produto.

        Raises:
            HTTPException: Se o produto já existir ou houver erro de validação.
        """
        try:
            product = self.create_product_use_case.execute(product_data)
            return product.dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def list_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Lista produtos por categoria.

        Args:
            category: A categoria para filtrar os produtos.

        Returns:
            Uma lista de produtos formatados.

        Raises:
            HTTPException: Se nenhum produto for encontrado na categoria.
        """
        products = self.list_products_by_category_use_case.execute(category)
        if not products:
            raise HTTPException(status_code=404, detail=f"No products found in category: {category}")
        return [product.dict() for product in products]

    def list_all_products(self) -> List[Dict[str, Any]]:
        """
        Lista todos os produtos disponíveis.

        Returns:
            Uma lista de produtos formatados.

        Raises:
            HTTPException: Se nenhum produto for encontrado.
        """
        products = self.list_all_products_use_case.execute()
        if not products:
            raise HTTPException(status_code=404, detail="No products found")
        return [product.dict() for product in products]

    def update_product(self, product_id: str, product_data: ProductSchema) -> Dict[str, Any]:
        """
        Atualiza um produto existente.

        Args:
            product_id: O ID do produto a ser atualizado.
            product_data: Os novos dados do produto.

        Returns:
            Uma resposta formatada contendo os detalhes atualizados do produto.

        Raises:
            HTTPException: Se o produto não for encontrado.
        """
        try:
            product = self.update_product_use_case.execute(product_id, product_data)
            return product.dict()
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    def delete_product(self, product_id: str) -> Dict[str, Any]:
        """
        Remove um produto pelo ID.

        Args:
            product_id: O ID do produto a remover.

        Returns:
            Uma mensagem de sucesso confirmando a remoção.

        Raises:
            HTTPException: Se o produto não for encontrado.
        """
        try:
            success = self.delete_product_use_case.execute(product_id)
            if not success:
                raise ValueError(f"Product with ID {product_id} not found or could not be deleted")
            return {"message": f"Product {product_id} deleted successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))