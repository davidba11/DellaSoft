import asyncio
from typing import List

from ..models.ProductStockModel import ProductStock
from ..repositories.ProductStockRepository import (
    select_all,
    insert_stock,
)


# ────────────────────────────────────────────────────────────────
#  SELECT
# ────────────────────────────────────────────────────────────────
async def select_all_stock_service() -> List[ProductStock]:
    """Obtiene todas las filas de `product_stock` en un *thread*
    para no bloquear el event-loop de Reflex."""
    return await asyncio.to_thread(select_all)


# ────────────────────────────────────────────────────────────────
#  INSERT
# ────────────────────────────────────────────────────────────────
async def insert_product_stock_service(
    *,
    product_id: int,
    quantity: float,
    min_quantity: float,
) -> ProductStock:
    """Crea el registro de stock para un **producto IN_STOCK**.

    ‣ Valida que no exista registro previo.  
    ‣ Ejecuta la operación en un *thread*.
    """
    row = ProductStock(
        product_id    = product_id,
        quantity      = quantity,
        min_quantity  = min_quantity,
    )
    return await asyncio.to_thread(insert_stock, row)
