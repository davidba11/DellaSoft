from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship

#Para evitar importaciones circulares
if TYPE_CHECKING:
    from .InvoiceModel import Invoice

if TYPE_CHECKING:
    from .POSModel import POS

if TYPE_CHECKING:
    from .CustomerModel import Customer

class Transaction(rx.Model, table=True):

    #Como la clase no se llama igual al archivo que la contiene, se agrega __tablename__
    __tablename__ = "transaction"

    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    observation: str = Field(nullable=True)
    amount: int = Field(nullable=False)
    transaction_date: datetime | None = Field(default=None, nullable=False)
    status: str = Field(nullable=False)
    id_invoice: int = Field(foreign_key="invoice.id")
    id_POS: int = Field(foreign_key="pos.id")
    id_user: int = Field(foreign_key="customer.id")

    #Se comenta que un customer puede tener 0 o 1 rol
    invoice: "Invoice" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="transactions"
    )

    pos: "POS" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="transactions"
    )

    customer: "Customer" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="transactions"
    )