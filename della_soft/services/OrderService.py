from ..repositories.OrderRepository import select_all, get_order, insert_order, update_order, update_pay_amount

from .CustomerService import select_by_id_service

from datetime import datetime

from ..models.OrderModel import Order


async def select_all_order_service():
    orders = select_all()
    return orders

def select_order(value: str):
    if(len(value) != 0):
        return get_order(value)
    else:
        return select_all()
    
def create_order(id: int, id_customer: int, observation: str, total_order: str, total_paid: str, order_date: datetime, delivery_date: datetime):

    order_save = Order(id=id, id_customer=id_customer, observation=observation, total_order=total_order, total_paid=total_paid, order_date=order_date, delivery_date=delivery_date)
    return insert_order(order_save)

def update_order_service(order: Order):
    return update_order(order)

def update_pay_amount_service(order: Order):
    return update_pay_amount(order)