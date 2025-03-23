from ..models.ProductOrderModel import ProductOrder
from .ConnectDB import connect
from sqlmodel import Session, select


def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(ProductOrder)
        return session.exec(query).all()