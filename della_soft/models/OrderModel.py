
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship

#Para evitar importaciones circulares
if TYPE_CHECKING:
    from .ProductOrderModel import ProductOrder

if TYPE_CHECKING:
    from .CustomerModel import Customer

class Order(rx.Model, table=True):

    #Como la clase no se llama igual al archivo que la contiene, se agrega __tablename__
    __tablename__ = "order"

    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    observation: str = Field(nullable=True)
    total_order: int | None = Field(default=None, nullable=False)
    total_paid: int | None = Field(default=None, nullable=False)
    order_date: datetime | None = Field(default=None, nullable=True)
    delivery_date: datetime | None = Field(default=None, nullable=True)
    id_customer: int = Field(foreign_key="customer.id") #Se declara FK de customer

    #Se comenta que un customer puede tener 0 o 1 rol
    order_detail: List["ProductOrder"] = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="order"
    )

    customer: "Customer" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="orders"
    )