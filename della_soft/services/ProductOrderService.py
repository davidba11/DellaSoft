from ..repositories.ProductOrderRespository import select_all, select_by_order_id, delete_product_order, insert_product_order
from ..models.ProductOrderModel import ProductOrder

def select_all_product_order_service():
    products_order = select_all()
    print (products_order)
    return products_order

def select_by_order_id_service(id_order: int):
    return select_by_order_id

def insert_product_order_service(orders: list[ProductOrder]):
        for order in orders:
            product_order = ProductOrder(id= orders.id, quantity= orders.quantity, id_product= orders.id_product, id_order = orders.id_order)
            var = insert_product_order(product_order)
            
def delete_product_order_service(id: int):
     return delete_product_order(id)