import reflex as rx

from sqlmodel import Field, create_engine, SQLModel

from .RolModel import Rol
from rxconfig import config



class Customer(rx.Model, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    first_name: str = Field(nullable=False)
    contact: str = Field(nullable=False)
    div: int | None = Field(default=None, nullable=True)
    username: str | None = Field(default=None, nullable=True)
    password: str | None = Field(default=None, nullable=True)
    id_rol: int | None = Field(default=None, nullable=True)

'''engine = create_engine(config.db_url, echo=True)

SQLModel.metadata.create_all(engine)'''