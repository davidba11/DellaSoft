# repositories/IngredientRepository.py
from sqlmodel import Session, select, or_
from .ConnectDB import connect
from ..models.IngredientModel import Ingredient

def select_all() -> list[Ingredient]:
    engine = connect()
    with Session(engine) as session:
        return session.exec(select(Ingredient)).all()

def get_ingredient(value: str) -> list[Ingredient]:   # 👈 quitar async
    engine = connect()
    with Session(engine) as session:
        query = select(Ingredient).where(
            or_(Ingredient.name.ilike(f"%{value}%"))
        )
        return session.exec(query).all()
    
def insert_ingredient(ingredient: Ingredient):
    engine = connect()
    with Session(engine) as session:
        session.add(ingredient)
        session.commit()
        query = select(Ingredient)
        return session.exec(query).all()