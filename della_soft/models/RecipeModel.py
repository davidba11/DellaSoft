import reflex as rx

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from sqlalchemy.orm import relationship
if TYPE_CHECKING:
    from .RecipeDetailModel import RecipeDetail
    from .ProductModel import Product

class Recipe (rx.Model, table=True):
    __tablename__ = "recipe"

    id: int = Field(default=None, primary_key=True)
    description: str
    id_product: int = Field(foreign_key="product.id")

    recipe_detail: List["RecipeDetail"] = Relationship(
        back_populates="recipe"
    )

    product: Optional["Product"] = Relationship(
        back_populates="recipe"
        
    )