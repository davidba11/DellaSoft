from datetime import datetime
from typing import List, TYPE_CHECKING
import reflex as rx
from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .OrderModel import Order
    from .StampedModel import Stamped
    from .TransactionModel import Transaction


class Invoice(rx.Model, table=True):

    __tablename__ = "invoice"

    id: int = Field(default=None, primary_key=True, nullable=False)

    iva: float = Field(nullable=False)
    invoice_date: datetime | None = Field(default=None)


    id_order: int   = Field(foreign_key="order.id")
    id_stamped: int | None = Field(foreign_key="stamped.id", nullable=False)

    order:   "Order"   = Relationship(back_populates="invoice")
    stamped: "Stamped" = Relationship(back_populates="invoices")

    nro_factura: str  = Field(nullable=False, max_length=20)
    pdf_hash:   str | None = Field(default=None, max_length=64)
    canceled:   bool = Field(default=False)