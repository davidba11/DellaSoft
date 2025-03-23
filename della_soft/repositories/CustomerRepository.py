from ..models.CustomerModel import Customer
from .ConnectDB import connect
from sqlmodel import Session, select

 
def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(Customer)
        return session.exec(query).all()
    
def select_by_name(name: str):
    engine = connect()
    with Session(engine) as session:
        query = select(Customer).where(Customer.first_name == name)
        return session.exec(query).all()
    
def select_by_id(id: int):
    engine = connect()
    with Session(engine) as session:
        query = select(Customer).where(Customer.id == id)
        return session.exec(query).all()
    
def create_customer(customer: Customer):
    engine = connect()
    with Session(engine) as session:
        session.add(customer)
        session.commit()
        query = select(Customer)
        return session.exec(query).all()