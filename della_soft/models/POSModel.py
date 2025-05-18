from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .TransactionModel import Transaction

class POS(rx.Model, table=True):
    __tablename__ = "pos"

    id: int = Field(default=None, primary_key=True, nullable=False)
    initial_amount: int = Field(nullable=False)
    final_amount: int = Field(nullable=False)
    pos_date: datetime | None = Field(default=None, nullable=True)

    transactions: Optional [List["Transaction"]] = Relationship(
        back_populates="pos"
    )