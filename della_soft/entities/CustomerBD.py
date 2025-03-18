import reflex as rx

from sqlmodel import SQLModel, Field

class CustomerBD(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    first_name: str = Field(nullable=False)
    contact: str = Field(nullable=False)
    div: int | None = Field(default=None, nullable=True)
    username: str | None = Field(default=None, nullable=True)
    password: str | None = Field(default=None, nullable=True)
    id_rol: int | None = Field(default=None, nullable=True, foreign_key="ROL.ID")