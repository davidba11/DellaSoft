import reflex as rx
from sqlmodel import Field, Relationship
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .MeasureModel import Measure
    from .IngredientStockModel import IngredientStock
    from .RecipeDetailModel import RecipeDetail


class Ingredient(rx.Model, table=True):
    __tablename__ = "ingredient"

    id: int = Field(primary_key=True, default=None)
    name: str = Field(nullable=False, unique=True)
    measure_id: int = Field(foreign_key="measure.id", nullable=False)

    # relaciones
    measure: "Measure" = Relationship(
        back_populates="ingredients"
    )

    stock_rows: Optional[List["IngredientStock"]] = Relationship(
        back_populates="ingredient"
    )

    recipe_details: Optional[List["RecipeDetail"]] = Relationship(
        back_populates="ingredient"
    )