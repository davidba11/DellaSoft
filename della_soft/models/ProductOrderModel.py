from typing import Optional, TYPE_CHECKING
import reflex as rx

from sqlmodel import Field, Relationship

#Para evitar importaciones circulares
if TYPE_CHECKING:
    from .ProductModel import Product
    from .OrderModel import Order

class ProductOrder(rx.Model, table=True):

    #Como la clase no se llama igual al archivo que la contiene, se agrega __tablename__
    __tablename__ = "product_order"

    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    quantity: int | None = Field(default=None, nullable=True)
    id_product: int = Field(foreign_key="product.id") #Se declara FK de producto
    id_order: int = Field(foreign_key="order.id") #Se declara FK de orden

    #Se comenta que un customer puede tener 0 o 1 rol
    order: "Order" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="order_detail"
    )

    product: "Product" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="product_detail"
    )