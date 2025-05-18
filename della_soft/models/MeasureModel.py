import reflex as rx
from sqlmodel import Field, Relationship
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .IngredientModel import Ingredient

class Measure(rx.Model, table=True):
    __tablename__ = "measure"

    id: int = Field(primary_key=True, default=None)
    description: str = Field(nullable=False, unique=True)

    ingredients: Optional[List["Ingredient"]] = Relationship(
        back_populates="measure"
    )