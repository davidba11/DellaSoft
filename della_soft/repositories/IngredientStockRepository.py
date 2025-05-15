# repositories/IngredientStockRepository.py
from typing import List, Optional

from sqlmodel import Session, select
from .ConnectDB import connect
from ..models.IngredientStockModel import IngredientStock


# ──────────────────────────────────────────────────────────────────────────────
def select_all() -> List[IngredientStock]:
    """Devuelve todas las filas de stock de ingredientes."""
    engine = connect()
    with Session(engine) as session:
        return session.exec(select(IngredientStock)).all()


# ──────────────────────────────────────────────────────────────────────────────
def get_by_ingredient(ingredient_id: int) -> Optional[IngredientStock]:
    """Devuelve la fila de stock de un ingrediente (o None si no existe)."""
    engine = connect()
    with Session(engine) as session:
        stmt = select(IngredientStock).where(
            IngredientStock.ingredient_id == ingredient_id
        )
        return session.exec(stmt).first()


# ──────────────────────────────────────────────────────────────────────────────
def insert_stock(stock_row: IngredientStock) -> IngredientStock:
    """
    Inserta una fila de stock.
    - Si ya existe un registro para ese ingrediente -> ValueError.
    """
    engine = connect()
    with Session(engine) as session:
        # ¿existe ya?
        if get_by_ingredient(stock_row.ingredient_id):
            raise ValueError(
                f"Ya existe stock para el ingrediente {stock_row.ingredient_id}"
            )

        session.add(stock_row)
        session.commit()
        session.refresh(stock_row)      # ← devuelve el objeto con su id
        return stock_row

def update_stock(
    stock_id: int,
    quantity: float,
    min_quantity: float
) -> IngredientStock:
    """Actualiza las cantidades de un stock de ingrediente."""
    engine = connect()
    with Session(engine) as session:
        db_row = session.get(IngredientStock, stock_id)
        if db_row is None:
            raise ValueError("Stock no encontrado")

        db_row.quantity     = quantity
        db_row.min_quantity = min_quantity
        session.add(db_row)
        session.commit()
        session.refresh(db_row)
        return db_row
