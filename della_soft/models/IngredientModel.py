
from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship


if TYPE_CHECKING:
    from .StockModel import Stock
    from .MeasureModel import Measure


class Ingredient(rx.Model, table=True):

    __tablename__ = "ingredient"

    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    name: str = Field(nullable=False)
    id_medida: int = Field(foreign_key="measure.id", nullable=False)

    measurement: "Measure" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="ingredients"
    )

    stock: Optional ["Stock"] = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="ingredient"
    )