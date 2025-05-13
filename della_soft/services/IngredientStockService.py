# services/IngredientStockService.py
import asyncio
from typing import List

from ..models.IngredientStockModel import IngredientStock
from ..repositories.IngredientStockRepository import (
    select_all,
    insert_stock,
)

# ──────────────────────────────────────────────────────────────────────────────
async def select_all_stock_service() -> List[IngredientStock]:
    """Devuelve todas las filas de stock de ingredientes (async)."""
    return await asyncio.to_thread(select_all)


# ──────────────────────────────────────────────────────────────────────────────
async def insert_ingredient_stock_service(
    ingredient_id: int,
    quantity: float,
    min_quantity: float,
):
    row = IngredientStock(
        ingredient_id = ingredient_id,   # ← aquí
        quantity      = quantity,
        min_quantity  = min_quantity,
    )
    return await asyncio.to_thread(insert_stock, row)
