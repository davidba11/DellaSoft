from ..models.MeasureModel import Measure
from .ConnectDB import connect
from sqlmodel import Session, or_, select

def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(Measure)
        return session.exec(query).all()
    
def select_by_id(id: int):
    engine = connect()
    with Session(engine) as session:
        query = select(Measure).where(Measure.id == id)
        return session.exec(query).all()