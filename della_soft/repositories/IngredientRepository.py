# repositories/IngredientRepository.py
from sqlmodel import Session, select, or_
from .ConnectDB import connect
from ..models.IngredientModel import Ingredient

from sqlalchemy.orm import joinedload
from sqlmodel import select, Session
from ..models.IngredientModel import Ingredient
from .ConnectDB import connect        # tu helper

def select_all(*, session: Session | None = None):
    own = session is None
    if own:
        engine = connect()
        session = Session(engine)
    try:
        stmt = (
            select(Ingredient)
            .options(joinedload(Ingredient.measure))   # 👈   eager-load unidad
            .order_by(Ingredient.name)
        )
        return list(session.exec(stmt))
    finally:
        if own:
            session.close()


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
    

def update_ingredient(ingredient: Ingredient):
    engine = connect()
    with Session(engine) as session:
        merged = session.merge(ingredient)  
        session.commit()
        session.refresh(merged)       
        return merged