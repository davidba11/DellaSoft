from della_soft.models.CustomerModel import Customer
from ..models.OrderModel import Order
from .ConnectDB import connect
from sqlmodel import Session, String, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession


def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(Order)
        return session.exec(query).all()
    
from sqlmodel import select, or_
from sqlalchemy.orm import joinedload
from sqlmodel.ext.asyncio.session import AsyncSession
from ..models.OrderModel import Order
from ..models.CustomerModel import Customer

def get_order(value: str):
    engine = connect()
    with Session(engine) as session:  # Usar sesión síncrona
        query = (
            select(Order)
            .join(Customer)  # Para hacer join con Customer si es necesario
            .where(
                or_(
                    Order.observation.ilike(f"%{value}%"),
                    Order.total_order.cast(String).ilike(f"%{value}%"),
                    Order.total_paid.cast(String).ilike(f"%{value}%"),
                    Order.order_date.cast(String).ilike(f"%{value}%"),
                    Order.delivery_date.cast(String).ilike(f"%{value}%"),
                    Customer.first_name.ilike(f"%{value}%"),  # Buscar por Cliente
                    Customer.last_name.ilike(f"%{value}%")
                )
            )
        )
        result = session.exec(query)
        return result.scalars().all()

    
def insert_order(order: Order) -> Order:
    engine = connect()
    with Session(engine) as session:
        session.add(order)
        session.commit()
        session.refresh(order)   # Trae el ID generado por la BD
        return order
    
def update_order(order: Order):
    engine = connect()
    with Session(engine) as session:
        merged = session.merge(order)  # merge devuelve la instancia vinculada a la sesión
        session.commit()
        session.refresh(merged)       # refrescamos la instancia que sí pertenece a la sesión
        return merged
    
def update_pay_amount(order: Order):
    engine = connect()
    with Session(engine) as session:
        # Traemos la instancia gestionada
        db_order = session.get(Order, order.id)
        if not db_order:
            raise ValueError(f"Pedido con id={order.id} no existe")
        # Cambiamos solo el campo que nos interesa
        db_order.total_paid = order.total_paid
        session.commit()
        return db_order