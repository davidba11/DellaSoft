from typing import List, Optional

from sqlmodel import Session, select

from .ConnectDB import connect
from ..models.ProductStockModel import ProductStock


# ────────────────────────────────────────────────────────────────
#  BÚSQUEDAS
# ────────────────────────────────────────────────────────────────
def select_all() -> List[ProductStock]:
    """Devuelve **todas** las filas de product_stock."""
    engine = connect()
    with Session(engine) as session:
        return session.exec(select(ProductStock)).all()


def get_by_product(product_id: int) -> Optional[ProductStock]:
    """Retorna la fila de stock que corresponde al producto
    (‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒)
    ‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒‒"""
    engine = connect()
    with Session(engine) as session:
        stmt = select(ProductStock).where(ProductStock.product_id == product_id)
        return session.exec(stmt).first()


# ────────────────────────────────────────────────────────────────
#  INSERCIÓN
# ────────────────────────────────────────────────────────────────
def insert_stock(stock_row: ProductStock) -> ProductStock:
    """Inserta una fila de stock **si el producto aún no la tiene**.

    Lanza `ValueError` cuando ya existe registro para el producto.
    """
    engine = connect()
    with Session(engine) as session:
        if get_by_product(stock_row.product_id):
            raise ValueError("Ya existe stock para ese producto.")

        session.add(stock_row)
        session.commit()
        session.refresh(stock_row)
        return stock_row
