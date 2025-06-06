from ..repositories.ProductOrderRepository import select_all, select_by_order_id, delete_product_order, insert_product_order, select_fixed_products
from ..models.ProductOrderModel import ProductOrder
from ..repositories.ProductOrderRepository import (
    insert_product_order as insert_repo_product_order,
)

def select_all_product_order_service():
    products_order = select_all()
    return products_order

def select_by_order_id_service(id_order: int):
    return select_by_order_id(id_order)

def get_fixed_products_by_order_id(order_id: int):
    products_order = select_fixed_products(order_id)
    return products_order

def insert_product_order_service(product_order: ProductOrder):
    return insert_repo_product_order(product_order)
            
def delete_product_order_service(id: int):
     return delete_product_order(id)

def update_product_orders(order_id: int, new_product_orders: list[ProductOrder]):
    existing = select_by_order_id(order_id)
    for po in existing:
        delete_product_order(po.id)
    for po in new_product_orders:
        insert_product_order(po)