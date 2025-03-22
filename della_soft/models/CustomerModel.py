from typing import Optional, TYPE_CHECKING
import reflex as rx

from sqlmodel import Field, Relationship

#Para evitar importaciones circulares
if TYPE_CHECKING:
    from .RolModel import Rol



    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    first_name: str = Field(nullable=False)
    contact: str = Field(nullable=False)
    div: int | None = Field(default=None, nullable=True)
    username: str | None = Field(default=None, nullable=True)
    password: str | None = Field(default=None, nullable=True)
    id_rol: int = Field(foreign_key="rol.id_rol") #Se declara FK de rol

    #Se comenta que un customer puede tener 0 o 1 rol
    rol: Optional["Rol"] = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="customers"
    )