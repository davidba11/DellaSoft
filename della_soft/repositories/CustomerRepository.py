from ..models.CustomerModel import Customer
from .ConnectDB import connect
from sqlmodel import Session, select, or_, String, func
#from ..views.CustomerView import offset, limit
from typing import TYPE_CHECKING

#def get_offset_limit():
#    from ..views.CustomerView import offset, limit
 #   return offset, limit
 
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
    
def get_total_items():
    engine = connect()
    with Session(engine) as session:
        query = select(func.count(Customer.id))  # Cuenta los registros de la tabla
        return session.exec(select(func.count(Customer.id))).one()

def get_customer_section(offset: int, limit: int):
    #offset, limit = get_offset_limit()
    engine = connect()
    with Session(engine) as session:
        #query= select(Customer)
        query = select(Customer).offset(offset).limit(limit)
        return session.exec(query).all()

def get_customer_section(offset: int, limit: int):
    """Obtiene una lista de clientes con paginación usando OFFSET y LIMIT."""
    engine = connect()
    with Session(engine) as session:
        query = select(Customer).offset(offset).limit(limit)
        return session.exec(query).all()










