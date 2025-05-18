from typing import Optional, TYPE_CHECKING
import reflex as rx

from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .ProductModel import Product
    from .OrderModel import Order

class ProductOrder(rx.Model, table=True):

    __tablename__ = "product_order"

    id: int = Field(default=None, primary_key=True, nullable=False)
    quantity: int | None = Field(default=None, nullable=True)
    id_product: int = Field(foreign_key="product.id")
    id_order: int = Field(foreign_key="order.id")

    order: "Order" = Relationship(
        back_populates="order_detail"
    )

    product: "Product" = Relationship(
        back_populates="product_detail"
    )