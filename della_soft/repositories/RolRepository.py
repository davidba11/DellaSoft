from ..models.RolModel import Rol
from .ConnectDB import connect
from sqlmodel import Session, select


def select_all():
    engine = connect()
    with Session(engine) as session:
        query = select(Rol)
        return session.exec(query).all()