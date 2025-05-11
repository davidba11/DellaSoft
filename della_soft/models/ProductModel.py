import reflex as rx
from sqlmodel import Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from enum import Enum
from decimal import Decimal
from sqlalchemy import Numeric   # ← para usar Decimal de forma correcta

if TYPE_CHECKING:
    from .ProductStockModel import ProductStock
    from .ProductOrderModel import ProductOrder


class ProductType(str, Enum):
    IN_STOCK = "Precio Fijo"      # se vende desde stock
    ON_DEMAND = "Precio Por Kilo" # se produce a pedido


class Product(rx.Model, table=True):
    __tablename__ = "product"

    id: int = Field(primary_key=True, default=None)
    name: str = Field(nullable=False, unique=True)
    description: str | None = Field(default=None)
    product_type: ProductType = Field(nullable=False)
    price: int = Field(nullable=False)

    stock_rows: Optional[List["ProductStock"]] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    product_detail: Optional[List["ProductOrder"]] = Relationship(
        back_populates="product"
    )
