# services/IngredientService.py
import asyncio
from ..repositories.IngredientRepository import select_all, get_ingredient, insert_ingredient
from ..models.IngredientModel import Ingredient

async def select_all_ingredient_service() -> list[Ingredient]:
    return await asyncio.to_thread(select_all)          # ✅

async def select_ingredient_service(value: str) -> list[Ingredient]:
    if value:
        return await asyncio.to_thread(get_ingredient, value)  # ✅
    else:
        return await asyncio.to_thread(select_all)             # ✅

def create_ingredient(id: int, name: str, id_medida: int):
    ingredient = Ingredient(id=id, name=name, id_medida=id_medida)
    return insert_ingredient(ingredient)