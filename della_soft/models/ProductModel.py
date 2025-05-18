import reflex as rx
from sqlmodel import Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from enum import Enum
from sqlalchemy import Column, Enum as SAEnum

if TYPE_CHECKING:
    from .ProductStockModel import ProductStock
    from .ProductOrderModel import ProductOrder
    from .RecipeModel import Recipe

class ProductType(str, Enum):
    IN_STOCK = "Precio Fijo"
    ON_DEMAND = "Precio Por Kilo"

class Product(rx.Model, table=True):
    __tablename__ = "product"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = Field(default=None)
    product_type: ProductType = Field(
        sa_column=Column(
            SAEnum(
                ProductType,
                values_callable=lambda enum_cls: [e.name for e in enum_cls],
                name="producttype",
            ),
            nullable=False,
        )
    )

    price: int = Field(nullable=False)

    stock_rows: Optional[List["ProductStock"]] = Relationship(
        back_populates="product"
    )

    product_detail: Optional[List["ProductOrder"]] = Relationship(
        back_populates="product"
    )

    recipe: Optional["Recipe"] = Relationship(
        back_populates="product"
    )