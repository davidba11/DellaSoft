from datetime import date, datetime
from ..models.POSModel import POS
from .ConnectDB import connect
from sqlmodel import Session, String, cast, exists, func, or_, select

def get_by_pos_date(value) -> POS | None:
    if isinstance(value, datetime):
        fecha = value.date()
    elif isinstance(value, date):
        fecha = value
    else:
        try:
            fecha = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            fecha = datetime.strptime(value, "%d/%m/%Y").date()
    engine = connect()
    with Session(engine) as session:
        stmt = select(POS).where(
            func.date(POS.pos_date) == fecha
        )
        return session.exec(stmt).first()
    
def insert_pos(pos: POS):
    engine = connect()
    with Session(engine) as session:
        session.add(pos)
        session.commit()

def update_pos(pos: POS):
    engine = connect()
    with Session(engine) as session:
        query = select(POS).where(POS.id == pos.id)
        c = session.exec(query).first()
        if c:
            c.initial_amount = pos.initial_amount
            c.final_amount = pos.final_amount
            c.pos_date = pos.pos_date
            session.add(c)
            session.commit()