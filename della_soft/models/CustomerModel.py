from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship

#Para evitar importaciones circulares
if TYPE_CHECKING:
    from .RolModel import Rol

if TYPE_CHECKING:
    from .OrderModel import Order

if TYPE_CHECKING:
    from .TransactionModel import Transaction

class Customer(rx.Model, table=True):

    #Como la clase no se llama igual al archivo que la contiene, se agrega _tablename_
    _tablename_ = "customer"

    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    ci: str = Field(nullable=True)
    contact: str = Field(nullable=False)
    div: int | None = Field(default=None, nullable=True)
    username: str | None = Field(default=None, nullable=True)
    password: str | None = Field(default=None, nullable=True)
    id_rol: int = Field(foreign_key="rol.id_rol", nullable=False) #Se declara FK de rol

    #Se comenta que un customer puede tener 0 o 1 rol
    rol: "Rol" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="customers"
    )

    orders: Optional [List["Order"]] = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="customer"
    )

    transactions: Optional [List["Transaction"]] = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="customer"
    )