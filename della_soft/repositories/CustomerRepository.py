from ..models.CustomerModel import Customer
from .ConnectDB import connect
from sqlmodel import Session, select, or_, String

 
def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(Customer)
        return session.exec(query).all()
    
def select_by_parameter(value: str):
    engine = connect()
    with Session(engine) as session:
        query = select(Customer).where(
            or_(
                Customer.first_name.ilike(f"%{value}%"),  # Busca coincidencias parciales en nombre
                Customer.last_name.ilike(f"%{value}%"),   # Busca coincidencias parciales en apellido
                Customer.id.cast(String).ilike(f"%{value}%"),
                Customer.contact.cast(String).ilike(f"%{value}%"),
                Customer.div.cast(String).ilike(f"%{value}%") # Convierte ID a string y busca coincidencias
            ))
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
    
def delete_customer(id: int):
    engine = connect()
    with Session(engine) as session:
        query = select(Customer).where(Customer.id == id)
        customer = session.exec(query).first()
        user_delete = session.exec(query).one()
        session.delete(user_delete)
        session.commit()
        return session.exec(query).all()