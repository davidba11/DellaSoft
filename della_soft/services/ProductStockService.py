import asyncio
from typing import List

from ..models.ProductStockModel import ProductStock
from ..repositories.ProductStockRepository import (
    select_all,
    insert_stock,
    update_stock,
    update_stock_with_pay,
    get_by_product,
    update_stock_with_reverse
)

async def select_all_stock_service() -> List[ProductStock]:
    return await asyncio.to_thread(select_all)

async def insert_product_stock_service( product_id: int, quantity: float, min_quantity: float) -> ProductStock:
    row = ProductStock(product_id = product_id, quantity = quantity, min_quantity = min_quantity)
    return await asyncio.to_thread(insert_stock, row)

async def update_product_stock_service(stock_id: int, quantity: float, min_quantity: float):
    return await asyncio.to_thread(update_stock, stock_id, quantity, min_quantity)

async def update_stock_with_pay_service(product_id: int, quantity: float):
    return await asyncio.to_thread(update_stock_with_pay, product_id, quantity)

async def update_stock_with_reverse_service(product_id: int, quantity: float):
    return await asyncio.to_thread(update_stock_with_reverse, product_id, quantity)

async def get_stock_by_product_service(product_id: int):
    return await asyncio.to_thread(get_by_product, product_id)
