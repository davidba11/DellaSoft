import reflex as rx

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .IngredientModel import Ingredient

class Measure (rx.Model, table=True):
    __tablename__ = "measure"

    id: int = Field(default=None, primary_key=True)
    description: str = Field(nullable=False)

    ingredients: Optional [List["Ingredient"]] = Relationship(
        back_populates="measurement"
    )
