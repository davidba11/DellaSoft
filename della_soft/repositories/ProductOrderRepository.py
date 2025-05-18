from sqlalchemy import and_
from ..models.ProductOrderModel import ProductOrder
from ..models.ProductModel import Product, ProductType
from .ConnectDB import connect
from sqlmodel import Session, or_, select


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
    
def select_fixed_products(id_order: int):
    engine = connect()
    with Session(engine) as session:
        stmt = (
            select(ProductOrder)
            .join(Product)
            .where(
                and_(
                    ProductOrder.id_order == id_order,
                    Product.product_type == ProductType.IN_STOCK.name
                )
            )
        )
        return session.exec(stmt).all()

def insert_product_order(product_order: ProductOrder) -> ProductOrder:
    engine = connect()
    with Session(engine) as session:
        session.add(product_order)
        session.commit()
        session.refresh(product_order)
        return product_order

def delete_product_order(id: int):
    engine = connect()
    with Session(engine) as session:
        query = select(ProductOrder).where(ProductOrder.id == id)
        customer = session.exec(query).first()
        user_delete = session.exec(query).one()
        session.delete(user_delete)
        session.commit()
        return session.exec(query).all()