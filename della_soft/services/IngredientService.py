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

def create_ingredient(id: int, name: str, measure_id: int):
    """Crea y guarda un ingrediente con la medida correcta."""
    ingredient = Ingredient(id=id, name=name, measure_id=measure_id)
    return insert_ingredient(ingredient)