import reflex as rx
from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .IngredientModel import Ingredient


class IngredientStock(rx.Model, table=True):
    __tablename__ = "ingredient_stock"

    id: int = Field(primary_key=True, default=None)
    ingredient_id: int = Field(foreign_key="ingredient.id", nullable=False)

    quantity: float = Field(nullable=False)     # cantidad actual
    min_quantity: float = Field(nullable=False) # punto de reposición

    ingredient: "Ingredient" = Relationship(back_populates="stock_rows")