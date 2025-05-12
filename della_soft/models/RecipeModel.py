import reflex as rx

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .RecipeDetailModel import RecipeDetail

class Recipe (rx.Model, table=True):
    __tablename__ = "recipe"

    id: int = Field(default=None, primary_key=True)
    description: str

    recipe_details: List["RecipeDetail"] = Relationship(
        back_populates="recipe"
    )
