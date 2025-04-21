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