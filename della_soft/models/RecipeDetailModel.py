from typing import Optional, TYPE_CHECKING
import reflex as rx

from sqlmodel import Field, Relationship

#Para evitar importaciones circulares
if TYPE_CHECKING:
    from .IngredientModel import Ingredient
    from .RecipeModel import Recipe

class RecipeDetail(rx.Model, table=True):

    #Como la clase no se llama igual al archivo que la contiene, se agrega __tablename__
    __tablename__ = "recipe_detail"

    id: int = Field(default=None, primary_key=True, nullable=False) #Se declara como PK
    quantity: int | None = Field(default=None, nullable=True)
    id_ingredient: int = Field(foreign_key="ingredient.id") #Se declara FK de producto
    id_recipe: int = Field(foreign_key="recipe.id") #Se declara FK de orden

    #Se comenta que un customer puede tener 0 o 1 rol
    recipe: "Recipe" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="recipe_details"
    )

    ingredient: "Ingredient" = Relationship(
        #Se declara como se llama la relación del otro lado (Debe ser igual a la otra clase)
        back_populates="recipe_details"
    )