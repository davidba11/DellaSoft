from ..models.OrderModel import Order
from .ConnectDB import connect
from sqlmodel import Session, or_, select


def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(Order)
        return session.exec(query).all()
    
def get_order(value: str):
    engine = connect()
    with Session(engine) as session:
        query = select(Order).where(
            or_(
                Order.id_customer.ilike(f"%{value}%"),  # Busca coincidencias parciales en nombre
                Order.order_date.ilike(f"%{value}%"),   # Busca coincidencias parciales descripción
                Order.delivery_date.ilike(f"%{value}%"),
            ))
        return session.exec(query).all()
    
def insert_order(order: Order):
    engine = connect()
    with Session(engine) as session:
        session.add(order)
        session.commit()
        query = select(Order)
        return session.exec(query).all()