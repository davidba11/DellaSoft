from datetime import date
from typing import List, TYPE_CHECKING
import reflex as rx
from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .InvoiceModel import Invoice


class Stamped(rx.Model, table=True):

    __tablename__ = "stamped"

    id: int = Field(default=None, primary_key=True, nullable=False)

    stamped_number: str = Field(nullable=False, max_length=15)
    establishment: str   = Field(nullable=False, max_length=3)
    expedition_point: str = Field(nullable=False, max_length=3)

    current_sequence: int = Field(default=0, nullable=False)
    max_sequence: int     = Field(nullable=False)

    date_from: date = Field(nullable=False)
    date_to:   date = Field(nullable=False)

    active: bool = Field(default=True)

    invoices: List["Invoice"] = Relationship(back_populates="stamped")