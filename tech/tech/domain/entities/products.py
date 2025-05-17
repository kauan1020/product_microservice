# tech/domain/entities/products.py
from datetime import datetime
from typing import Optional


class Products:
    """
    Representa um produto no sistema.

    Mantém exatamente a mesma estrutura da classe original para garantir
    compatibilidade total com o código existente.
    """

    def __init__(self, name: str, price: float, category: str, id: Optional[str] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def dict(self):
        """
        Retorna uma representação em dicionário para API.
        Este método já existia na implementação original.
        """
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }