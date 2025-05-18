
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
import reflex as rx

from sqlmodel import Field, Relationship

if TYPE_CHECKING:
    from .ProductOrderModel import ProductOrder

if TYPE_CHECKING:
    from .CustomerModel import Customer

if TYPE_CHECKING:
    from .InvoiceModel import Invoice

if TYPE_CHECKING:
    from .TransactionModel import Transaction

class Order(rx.Model, table=True):
    __tablename__ = "order"

    id: int = Field(default=None, primary_key=True, nullable=False)
    observation: str = Field(nullable=True)
    total_order: int | None = Field(default=None, nullable=False)
    total_paid: int | None = Field(default=None, nullable=False)
    order_date: datetime | None = Field(default=None, nullable=True)
    delivery_date: datetime | None = Field(default=None, nullable=True)
    id_customer: int = Field(foreign_key="customer.id")

    order_detail: List["ProductOrder"] = Relationship(
        back_populates="order"
    )

    customer: "Customer" = Relationship(
        back_populates="orders"
    )

    invoice: "Invoice" = Relationship(
        back_populates="order"
    )

    transactions: Optional[List["Transaction"]] = Relationship(
        back_populates="order"
    )