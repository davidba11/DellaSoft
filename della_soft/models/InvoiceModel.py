from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .OrderModel import Order

if TYPE_CHECKING:
    from .TransactionModel import Transaction

class Invoice(rx.Model, table=True):
    __tablename__ = "invoice"

    id: int = Field(default=None, primary_key=True, nullable=False)
    iva: float = Field(nullable=False)
    invoice_date: datetime | None = Field(default=None, nullable=True)
    id_order: int = Field(foreign_key="order.id")

    order: "Order" = Relationship(
        back_populates="invoice"
    )