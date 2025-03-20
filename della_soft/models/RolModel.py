import reflex as rx

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .CustomerModel import Customer

class Rol (rx.Model, table=True):
    __tablename__ = "rol"

    id_rol: Optional[int] = Field(default=None, primary_key=True)
    description: str

    customers: List["Customer"] = Relationship(
        back_populates="rol"
    )
