from ..models.ProductModel import Product
from .ConnectDB import connect
from sqlmodel import Session, or_, select


def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(Product)
        return session.exec(query).all()
    
def insert_product(product: Product):
    engine = connect()
    with Session(engine) as session:
        session.add(product)
        session.commit()
        query = select(Product)
        return session.exec(query).all()
    
def get_product(value: str):
    engine = connect()
    with Session(engine) as session:
        query = select(Product).where(
            or_(
                Product.name.ilike(f"%{value}%"),  # Busca coincidencias parciales en nombre
                Product.description.ilike(f"%{value}%"),   # Busca coincidencias parciales descripción
                Product.product_type.ilike(f"%{value}%"),
            ))
        return session.exec(query).all()
    
def get_by_id(id: int):
    engine = connect()
    with Session(engine) as session:
        query = select(Product).where(Product.id == id)
        return session.exec(query).all()
    
def delete_product(id: int):
    engine = connect()
    with Session(engine) as session:
        query = select(Product).where(Product.id == id)
        customer = session.exec(query).first()
        user_delete = session.exec(query).one()
        session.delete(user_delete)
        session.commit()
        return session.exec(query).all()