from ..repositories.OrderRepository import select_all, get_order, insert_order

from .CustomerService import select_by_id_service, select_by_name_service

from datetime import datetime

from ..models.OrderModel import Order


async def select_all_order_service():
    orders = await select_all()
    return orders

async def select_order(value: str):
    if len(value) != 0:
        return await get_order(value)  
    else:
        return select_all()
    
def create_order(id: int, customer_name: str, observation: str, total_order: float, total_paid: float, order_date: datetime, delivery_date: datetime):
    # Buscar el cliente por nombre
    customer = select_by_name_service(customer_name)  # Busca por nombre o apellido

    if customer:
        # Si el cliente es encontrado, usamos su id
        id_customer = customer.id
        # Crear el pedido
        order_save = Order(
            id=id,  # Si tu base de datos maneja auto increment en el ID, déjalo como None
            id_customer=id_customer,
            observation=observation,
            total_order=total_order,
            total_paid=total_paid,
            order_date=order_date,
            delivery_date=delivery_date
        )
        return insert_order(order_save)
    else:
        # Si no se encuentra el cliente
        raise ValueError(f"Cliente con nombre {customer_name} no encontrado.")