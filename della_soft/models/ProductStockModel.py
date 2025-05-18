import reflex as rx
from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ProductModel import Product

class ProductStock(rx.Model, table=True):
    __tablename__ = "product_stock"

    id: int = Field(primary_key=True, default=None)
    product_id: int = Field(foreign_key="product.id", nullable=False)

    quantity: int = Field(nullable=False)
    min_quantity: int = Field(nullable=False)

    product: "Product" = Relationship(back_populates="stock_rows")