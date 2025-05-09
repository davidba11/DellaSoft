from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship

#Con productopedido
if TYPE_CHECKING:
    from .ProductOrderModel import ProductOrder
    from .CustomerModel import Customer
    from .StockModel import Stock

class Product(rx.Model, table=True):

    __tablename__ = "product"

    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    product_type: str = Field(default=None, nullable=False)
    price: int = Field (default=0, nullable=False)

    product_detail: List["ProductOrder"] = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="product"
    )

    stock: Optional["Stock"] = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="products"
    )