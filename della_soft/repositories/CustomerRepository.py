from ..models.CustomerModel import Customer
from .ConnectDB import connect
from sqlmodel import Session, select


def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(Customer)
        return session.exec(query).all()