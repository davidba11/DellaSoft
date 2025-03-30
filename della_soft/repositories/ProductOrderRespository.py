from ..models.ProductOrderModel import ProductOrder
from .ConnectDB import connect
from sqlmodel import Session, select


def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(ProductOrder)
        return session.exec(query).all()

def select_by_order_id(id_order: int):
    engine = connect()
    with Session(engine) as session:
        query = select(ProductOrder).where(ProductOrder.id_order == id_order)
        return session.exec(query).all()

def insert_product_order(product_order: ProductOrder):
    engine = connect()
    with Session(engine) as session:
        session.add(product_order)
        session.commit()
        query = select(product_order).where(ProductOrder.id_order == product_order.id_order)
        return session.exec(query).all()

def delete_product_order(id: int):
    engine = connect()
    with Session(engine) as session:
        query = select(ProductOrder).where(ProductOrder.id == id)
        customer = session.exec(query).first()
        user_delete = session.exec(query).one()
        session.delete(user_delete)
        session.commit()
        return session.exec(query).all()