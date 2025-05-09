import reflex as rx

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .IngredientModel import Ingredient
    from .ProductModel import Product

class Stock (rx.Model, table=True):
    __tablename__ = "stock"

    id: int = Field(default=None, primary_key=True)
    cant: int = Field(nullable=False)
    cant_min: int = Field(nullable=False)

    ingredients: Optional [List["Ingredient"]] = Relationship(
        back_populates="stock"
    )

    products: Optional [List["Product"]] = Relationship(
        back_populates="stock"
    )


