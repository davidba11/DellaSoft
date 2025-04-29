from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .TransactionModel import Transaction

class POS(rx.Model, table=True):

    #Como la clase no se llama igual al archivo que la contiene, se agrega __tablename__
    __tablename__ = "pos"

    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    initial_amount: int = Field(nullable=False)
    final_amount: int = Field(nullable=False)
    pos_date: datetime | None = Field(default=None, nullable=True)

    #Se comenta que un customer puede tener 0 o 1 rol
    transactions: Optional [List["Transaction"]] = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="pos"
    )