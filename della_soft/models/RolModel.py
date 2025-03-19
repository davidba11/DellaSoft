import reflex as rx

from typing import Optional
from sqlmodel import Field


from rxconfig import config

class Rol (rx.Model, table=True):
    id_rol: Optional[int] = Field(default=None, primary_key=True)
    description: str

'''engine = create_engine(config.db_url, echo=True)
SQLModel.metadata.create_all(engine)'''
