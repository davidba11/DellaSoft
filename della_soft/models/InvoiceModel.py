from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship

#Para evitar importaciones circulares
if TYPE_CHECKING:
    from .OrderModel import Order

if TYPE_CHECKING:
    from .TransactionModel import Transaction

class Invoice(rx.Model, table=True):

    #Como la clase no se llama igual al archivo que la contiene, se agrega __tablename__
    __tablename__ = "invoice"

    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    iva: float = Field(nullable=False)
    invoice_date: datetime | None = Field(default=None, nullable=True)
    id_order: int = Field(foreign_key="order.id") #Se declara FK de customer

    #Se comenta que un customer puede tener 0 o 1 rol
    order: "Order" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="invoice"
    )