from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .POSModel import POS

if TYPE_CHECKING:
    from .CustomerModel import Customer

if TYPE_CHECKING:
    from .OrderModel import Order

class Transaction(rx.Model, table=True):

    #Como la clase no se llama igual al archivo que la contiene, se agrega __tablename__
    __tablename__ = "transaction"

    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    observation: str = Field(nullable=True)
    amount: int = Field(nullable=False)
    transaction_date: datetime | None = Field(default=None, nullable=False)
    status: str = Field(nullable=False)
    id_POS: int = Field(foreign_key="pos.id")
    id_user: int = Field(foreign_key="customer.id")
    id_order: int = Field(foreign_key="order.id", nullable=True)

    pos: "POS" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="transactions"
    )

    customer: "Customer" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="transactions"
    )

    order: Optional["Order"] = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="transactions"
    )