from ..models.ProductModel import Product
from .ConnectDB import connect
from sqlmodel import Session, select


def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(Product)
        return session.exec(query).all()