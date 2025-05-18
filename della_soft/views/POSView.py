import reflex as rx
from typing import Optional, List

from rxconfig import config

from ..services.SystemService import (
    get_sys_date_two,
    get_sys_date_to_string_two,
    get_sys_date_three,
)
from ..repositories.LoginRepository import AuthState
from ..services.POSService import POS_is_open, insert_pos_register, update_final_amount
from ..services.OrderService import select_all_order_service, update_pay_amount_service
from ..services.CustomerService import select_name_by_id
from ..services.ProductOrderService import get_fixed_products_by_order_id
from ..services.ProductStockService import update_stock_with_pay_service, get_stock_by_product_service
from ..models.POSModel import POS
from ..models.OrderModel import Order
from ..services.TransactionService import create_transaction
from ..models.TransactionModel import Transaction
from datetime import datetime

from .OrderView import OrderView, view_order_modal

def render_row(item: dict) -> rx.Component:
    order_id      = item["id"]
    customer_name = item["customer_name"]
    total_paid    = item["total_paid"]
    pending       = item["pending"]
    total_order   = item["total_order"]

    return rx.table.row(
        rx.table.cell(rx.text(order_id)),
        rx.table.cell(rx.text(customer_name)),
        rx.table.cell(
            rx.cond(
                total_paid == total_order,
                rx.text("PAGADO"),
                rx.text("FALTA PAGO"),
            )
        ),
        rx.table.cell(rx.text(pending)),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("eye", size=22),
                    on_click=OrderView.open_view_modal(order_id),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    title="Ver Pedido",
                ),
                rx.cond(
                    total_paid == total_order,
                    rx.cond(
                        OrderView.pdf_url != "",
                        rx.link(
                            rx.icon("file-text", size=22),
                            href=OrderView.pdf_url,
                            target="_blank",
                            title="Ver Factura",
                        ),
                        rx.button(
                            rx.icon("file-text", size=22),
                            on_click=OrderView.generate_invoice_pdf_event(order_id),
                            background_color="#3E2723",
                            size="2",
                            variant="solid",
                            title="Ver Factura",
                        ),
                    ),
                    payment_dialog_component(
                        order_id, total_paid, pending, total_order
                    ),
                ),
                rx.cond(
                    total_paid != 0,
                    reverse_dialog_component(
                        order_id, total_paid, pending, total_order
                    ),
                ),
                spacing="2",
            )
        ),
        color="#3E2723",
    )

def get_table_header() -> rx.Component:
    return rx.table.row(
        rx.table.column_header_cell("ID"),
        rx.table.column_header_cell("Cliente"),
        rx.table.column_header_cell("¿Pagado Totalmente?"),
        rx.table.column_header_cell("Monto a Pagar"),
        rx.table.column_header_cell("Acciones"),
        color="#3E2723",
        background_color="#A67B5B",
    )

class POSView(rx.State):
    show_paid: bool = False
    sys_date: str
    is_open: bool = False
    final_amount: float = 0.0
    pos: Optional[POS] = None

    pos_search: str = ""
    pos_data: List[dict] = []
    filtered_pos_data: List[dict] = []
    offset_pos: int = 0
    limit_pos: int = 5
    total_items_pos: int = 0

    payment_amount: int = 0
    max_payment: int = 0
    is_payment_invalid: bool = False
    payment_error: str = ""

    @rx.event
    def toggle_show_paid(self, checked: bool):
        self.show_paid = checked
        self.apply_filters()

    def apply_filters(self):
        data = list(self.pos_data)
        if not self.show_paid:
            data = [o for o in data if o["pending"] > 0]
        q = (self.pos_search or "").strip().lower()
        if q:
            filtered = []
            for o in data:
                estado = "pagado" if o["total_paid"] == o["total_order"] else "falta pago"
                if (
                    q in str(o["id"]).lower()
                    or q in o["customer_name"].lower()
                    or q in estado
                    or q in str(o["pending"])
                ):
                    filtered.append(o)
            data = filtered
        self.filtered_pos_data = data
        self.total_items_pos = len(data)
        self.offset_pos = 0
        self.set()

    @rx.event
    def set_payment_context(self, pending: int):
        self.payment_amount = pending
        self.max_payment = pending
        self.is_payment_invalid = False
        self.payment_error = ""
        self.set()

    @rx.event
    def set_reverse_context(self, order_id: int, total_paid: int):
        self.max_payment = total_paid
        self.payment_amount = -total_paid
        self.is_payment_invalid = False
        self.payment_error = ""
        self.set()

    @rx.event
    def validate_payment(self, value: str):
        text = (value or "").strip()
        if text == "":
            self.payment_amount = 0
            self.is_payment_invalid = True
            self.payment_error = "Monto a Pagar no puede ser vacío"
        else:
            try:
                amt = int(text)
            except ValueError:
                amt = 0
            self.payment_amount = amt
            if amt <= 0:
                self.is_payment_invalid = True
                self.payment_error = "Monto a Pagar no puede ser cero (0)"
            elif amt > self.max_payment:
                self.is_payment_invalid = True
                self.payment_error = "Monto a Pagar no puede superar el Monto Faltante"
            else:
                self.is_payment_invalid = False
                self.payment_error = ""
        self.set()

    @rx.event
    def validate_reverse(self, value: str):
        text = (value or "").strip()
        if text == "":
            self.payment_amount = 0
            self.is_payment_invalid = True
            self.payment_error = "Monto a Reversar no puede ser vacío"
        else:
            try:
                amt = int(text)
            except ValueError:
                amt = 0
            if amt >= 0:
                self.is_payment_invalid = True
                self.payment_error = "Monto a reversar debe ser negativo"
                self.payment_amount = 0
            else:
                self.payment_amount = amt
                if abs(amt) > self.max_payment:
                    self.is_payment_invalid = True
                    self.payment_error = "Monto a reversar no puede superar el monto pagado"
                else:
                    self.is_payment_invalid = False
                    self.payment_error = ""
        self.set()

    @rx.event
    def validate_bill(self, value: str):
        text = (value or "").strip()
        if text == "":
            self.payment_amount = 0
            self.is_payment_invalid = True
            self.payment_error = "Monto Gastado no puede ser vacío"
        else:
            try:
                amt = int(text)
            except ValueError:
                amt = 0
            if amt >= 0:
                self.payment_amount = 0
                self.is_payment_invalid = True
                self.payment_error = "El monto gastado debe ser negativo"
            elif abs(amt) > (self.pos.final_amount if self.pos else 0):
                self.payment_amount = amt
                self.is_payment_invalid = True
                self.payment_error = "Monto Gastado no puede superar el monto final"
            else:
                self.payment_amount = amt
                self.is_payment_invalid = False
                self.payment_error = ""
        self.set()

    @rx.event
    def on_pos_search(self, value: str):
        self.pos_search = (value or "").strip().lower()
        self.apply_filters()

    @rx.event
    def pos_prev_page(self):
        if self.offset_pos > 0:
            self.offset_pos -= self.limit_pos
        self.set()

    @rx.event
    def pos_next_page(self):
        if self.offset_pos + self.limit_pos < self.total_items_pos:
            self.offset_pos += self.limit_pos
        self.set()

    @rx.var
    def num_total_pages_pos(self) -> int:
        return max((self.total_items_pos + self.limit_pos - 1) // self.limit_pos, 1)

    @rx.var
    def current_page_pos(self) -> int:
        return (self.offset_pos // self.limit_pos) + 1

    @rx.var
    def pos_page_data(self) -> List[dict]:
        return self.filtered_pos_data[self.offset_pos : self.offset_pos + self.limit_pos]

    @rx.event
    async def load_date(self):
        self.sys_date = get_sys_date_to_string_two()
        self.pos = POS_is_open(get_sys_date_two(self.sys_date))
        self.is_open = self.pos is not None
        orders = await select_all_order_service()
        self.pos_data = [
            {
                "id": o.id,
                "customer_name": select_name_by_id(o.id_customer),
                "total_order": o.total_order,
                "total_paid": o.total_paid,
                "pending": o.total_order - o.total_paid,
            }
            for o in orders
        ]
        self.pos_search = ""
        self.show_paid = False
        self.apply_filters()

    @rx.var
    def get_initial_amount(self) -> int:
        return self.pos.initial_amount if self.pos else 0

    @rx.var
    def get_final_amount(self) -> int:
        return self.pos.final_amount if self.pos else 0

    @rx.var
    def get_earnings(self) -> int:
        return (self.pos.final_amount - self.pos.initial_amount) if self.pos else 0

    @rx.event
    def on_initial_amount_change(self, value: str):
        try:
            self.final_amount = float(value)
        except ValueError:
            self.final_amount = 0.0
        self.set()

    @rx.var
    def get_status_label(self) -> str:
        return "ABIERTO" if self.is_open else "CERRADO"

    @rx.event
    async def insert_pos_controller(self, form_data: dict):
        form_data["pos_date"] = get_sys_date_three(form_data["pos_date"])
        try:
            insert_pos_register(
                id="",
                initial_amount=form_data["initial_amount"],
                final_amount=form_data["final_amount"],
                pos_date=form_data["pos_date"],
            )
            yield POSView.load_date()
        except BaseException as e:
            print(e.args)

    @rx.event
    async def process_payment(self, form_data: dict):
        order_id = int(form_data.get("order_id", 0))
        amount   = int(form_data.get("pending", 0))
        auth = await self.get_state(AuthState)
        user_id = auth.current_user_id
        if user_id is None:
            yield rx.toast("Sesión expirada. Vuelve a iniciar sesión")
            return

        order = next((o for o in self.pos_data if o["id"] == order_id), None)
        if not order:
            print(f"Pedido {order_id} no encontrado")
            return

        fixed_products = get_fixed_products_by_order_id(order_id)

        for po in fixed_products:
            stock_row = await get_stock_by_product_service(po.id_product)
            if stock_row is None or stock_row.quantity < po.quantity:
                yield rx.toast("Cantidad en stock superado. Favor reabastecer stock para continuar")
                self.is_payment_invalid = True
                self.payment_error = (
                    f"Stock insuficiente para el producto ID {po.id_product} "
                    f"(disponible: {stock_row.quantity if stock_row else 0}, "
                    f"solicitado: {po.quantity})"
                )
                self.set()
                return

        new_total_paid = order["total_paid"] + amount
        try:
            create_transaction(
                Transaction(
                    id=None,
                    observation=f"Pago por {amount}",
                    amount=amount,
                    transaction_date=datetime.now(),
                    status="PAGO",
                    id_POS=self.pos.id,
                    id_user=user_id,
                    id_order=order_id,
                )
            )
            update_pay_amount_service(Order(id=order_id, total_paid=new_total_paid))
        except Exception as e:
            print("Error al procesar pago/registro de transacción:", e)
            return

        update_final_amount(
            self.pos.id,
            self.pos.initial_amount,
            self.pos.final_amount + amount,
            self.pos.pos_date,
        )

        if new_total_paid >= order["total_order"]:
            try:
                for po in fixed_products:
                    await update_stock_with_pay_service(po.id_product, po.quantity)
            except Exception as e:
                print("Error al actualizar stock:", e)

        if amount == order["pending"]:
            yield OrderView.generate_invoice_pdf_event(order_id)
        yield POSView.load_date()

    @rx.event
    async def process_reverse(self, form_data: dict):
        order_id = int(form_data.get("order_id", 0))
        amount   = int(form_data.get("reverse_amount", 0))
        auth = await self.get_state(AuthState)
        user_id = auth.current_user_id
        if user_id is None:
            yield rx.toast("Sesión expirada. Vuelve a iniciar sesión")
            return
        order = next((o for o in self.pos_data if o["id"] == order_id), None)
        if not order:
            print(f"Pedido {order_id} no encontrado")
            return

        new_total_paid = order["total_paid"] + amount
        try:
            create_transaction(
                Transaction(
                    id=None,
                    observation=f"Reverso de {amount}",
                    amount=amount,
                    transaction_date=datetime.now(),
                    status="REVERSO",
                    id_POS=self.pos.id,
                    id_user=user_id,
                    id_order=order_id,
                )
            )
            update_pay_amount_service(Order(id=order_id, total_paid=new_total_paid))
        except Exception as e:
            print("Error al procesar reverso:", e)
            return
        update_final_amount(
            self.pos.id,
            self.pos.initial_amount,
            self.pos.final_amount + amount,
            self.pos.pos_date,
        )
        yield POSView.load_date()

    @rx.event
    async def process_bill(self, form_data: dict):
        amount = int(form_data.get("bill_amount", 0))
        observation = form_data.get("observation", "").strip()
        auth = await self.get_state(AuthState)
        user_id = auth.current_user_id
        if user_id is None:
            yield rx.toast("Sesión expirada. Vuelve a iniciar sesión")
            return
        try:
            create_transaction(
                Transaction(
                    id=None,
                    observation=observation,
                    amount=amount,
                    transaction_date=datetime.now(),
                    status="GASTO",
                    id_POS=self.pos.id,
                    id_user=user_id,
                    id_order=None,
                )
            )
            update_final_amount(
                self.pos.id,
                self.pos.initial_amount,
                self.pos.final_amount + amount,
                self.pos.pos_date,
            )
        except Exception as e:
            print("Error al ingresar gasto:", e)
            return
        yield POSView.load_date()

def get_title() -> rx.Component:
    return rx.text(
        "Caja",
        size="7",
        weight="bold",
        color="#3E2723",
        high_contrast=True,
        fontFamily="DejaVu Sans Mono",
        width="80%",
    ),


def create_pos_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.grid(
                rx.text("Monto Inicial:", color="white"),
                rx.cond(
                    POSView.is_open,
                    rx.input(
                        placeholder="Monto Inicial",
                        name="initial_amount",
                        type="number",
                        background_color="#5D4037",
                        placeholder_color="white",
                        color="white",
                        width="100%",
                        value=POSView.get_initial_amount,
                        read_only=True,
                    ),
                    rx.input(
                        placeholder="Monto Inicial",
                        name="initial_amount",
                        type="number",
                        background_color="#3E2723",
                        placeholder_color="white",
                        color="white",
                        width="100%",
                        default_value="0",
                        on_change=POSView.on_initial_amount_change,
                    ),
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Monto Final:", color="white"),
                rx.cond(
                    POSView.is_open,
                    rx.input(
                        name="final_amount",
                        value=POSView.get_final_amount,
                        read_only=True,
                        type="number",
                        background_color="#5D4037",
                        placeholder_color="white",
                        color="white",
                        width="100%",
                    ),
                    rx.input(
                        name="final_amount",
                        value=POSView.final_amount,
                        read_only=True,
                        type="number",
                        background_color="#5D4037",
                        placeholder_color="white",
                        color="white",
                        width="100%",
                    ),
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Estado:", color="white"),
                rx.select(
                    ["CERRADO", "ABIERTO"],
                    value=POSView.get_status_label,
                    name="status",
                    read_only=True,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                    disabled=True,
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Fecha:", color="white"),
                rx.input(
                    name="pos_date",
                    value=POSView.sys_date,
                    read_only=True,
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            rx.cond(
                POSView.is_open,
                rx.grid(
                    rx.text("Ganancias del día:", color="white"),
                    rx.input(
                        name="earnings",
                        value=POSView.get_earnings,
                        read_only=True,
                        type="number",
                        background_color="#5D4037",
                        placeholder_color="white",
                        color="white",
                        width="100%",
                    ),
                    columns="1fr 2fr",
                    gap="3",
                    width="100%",
                ),
                rx.dialog.close(
                    rx.button(
                        rx.icon("save", size=22),
                        type="submit",
                        background_color="#3E2723",
                        color="white",
                        size="2",
                        variant="solid",
                    )
                ),
            ),
            spacing="3",
        ),
        on_submit=POSView.insert_pos_controller,
        align="center",
        justify="center",
        style={"width": "100%", "gap": "3", "padding": "3"},
    )

def create_bill_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.grid(
                rx.text("Monto Inicial:", color="white"),
                rx.input(
                        placeholder="Monto Inicial",
                        name="initial_amount",
                        type="number",
                        background_color="#5D4037",
                        placeholder_color="white",
                        color="white",
                        width="100%",
                        value=POSView.get_initial_amount,
                        read_only=True,
                    ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Monto Final:", color="white"),
                rx.input(
                    name="final_amount",
                    value=POSView.get_final_amount,
                    read_only=True,
                    type="number",
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Estado:", color="white"),
                rx.select(
                    ["CERRADO", "ABIERTO"],
                    value=POSView.get_status_label,
                    name="status",
                    read_only=True,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Fecha:", color="white"),
                rx.input(
                    name="pos_date",
                    value=POSView.sys_date,
                    read_only=True,
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Monto Gastado:", color="white"),
                rx.input(
                    name="bill_amount",
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                    default_value="0",
                    on_change=POSView.validate_bill,
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Observación:", color="white"),
                rx.text_area(name="observation", background_color="#5D4037", color="white", rows="3"),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            rx.grid(
                rx.text("Ganancias del día:", color="white"),
                rx.input(
                    name="earnings",
                    value=POSView.get_earnings,
                    read_only=True,
                    type="number",
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        rx.icon("save", size=22),
                        type="submit",
                        disabled=POSView.is_payment_invalid,
                        background_color="#3E2723",
                        color="white",
                        size="2",
                        variant="solid",
                    )
                ),
                rx.cond(
                    POSView.is_payment_invalid,
                    rx.text(f"{POSView.payment_error}", color="white"),
                    rx.text(""),
                ),
                spacing="2",
                align="center",
            ),
            spacing="3",
        ),
        on_submit=POSView.process_bill,
        align="center",
        justify="center",
        style={"width": "100%", "gap": "3", "padding": "3"},
    )

def open_pos_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.cond(
                    POSView.is_open,
                    rx.text("Ver Caja"),
                    rx.text("Abrir Caja"),
                ),
                background_color="#3E2723",
                size="2",
                variant="solid",
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.cond(
                    POSView.is_open,
                    rx.dialog.title("Ver Caja"),
                    rx.dialog.title("Abrir Caja"),
                ),
                create_pos_form(),
                direction="column",
                align="center",
                justify="center",
                gap="4",
            ),
            background_color="#A67B5B",
        ),
        style={"width": "320px"},
    )

def open_bills_modal() -> rx.Component:
    return rx.cond(
        POSView.is_open,
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button(
                    rx.text("Ingresar Gasto"),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                )
            ),
            rx.dialog.content(
                rx.flex(
                    rx.dialog.title("Ingresar Gasto"),
                    create_bill_form(),
                    direction="column",
                    align="center",
                    justify="center",
                    gap="4",
                ),
                background_color="#A67B5B",
            ),
            style={"width": "320px"},
        ),
    )

def update_payment_form(order_id: int, total_paid: int, pending: int, total_order: int) -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(name="order_id", type="hidden", default_value=order_id),
            rx.grid(
                rx.text("Pagado:", color="white"),
                rx.input(
                    name="total_paid",
                    type="number",
                    default_value=total_paid,
                    read_only=True,
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Faltante:", color="white"),
                rx.input(
                    name="pending_amount",
                    type="number",
                    default_value=pending,
                    read_only=True,
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Total:", color="white"),
                rx.input(
                    name="total_order",
                    type="number",
                    default_value=total_order,
                    read_only=True,
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Monto a Pagar:", color="white"),
                rx.input(
                    name="pending",
                    type="number",
                    default_value=pending,
                    on_change=POSView.validate_payment,
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        rx.icon("save", size=22),
                        type="submit",
                        disabled=POSView.is_payment_invalid,
                        background_color="#3E2723",
                        size="2",
                        variant="solid",
                    )
                ),
                rx.cond(
                    POSView.is_payment_invalid,
                    rx.text(f"{POSView.payment_error}", color="white"),
                    rx.text(""),
                ),
                spacing="2",
            ),
        ),
        on_submit=POSView.process_payment,
        style={"width": "100%", "gap": "3", "padding": "3"},
        align="center",
        justify="center",
    )

def update_reverse_form(order_id: int, total_paid: int, pending: int, total_order: int) -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(name="order_id", type="hidden", default_value=order_id),
            rx.grid(
                rx.text("Pagado:", color="white"),
                rx.input(
                    name="total_paid",
                    type="number",
                    default_value=total_paid,
                    read_only=True,
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Faltante:", color="white"),
                rx.input(
                    name="pending_amount",
                    type="number",
                    default_value=pending,
                    read_only=True,
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Total:", color="white"),
                rx.input(
                    name="total_order",
                    type="number",
                    default_value=total_order,
                    read_only=True,
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Monto a Reversar:", color="white"),
                rx.input(
                    name="reverse_amount",
                    type="number",
                    value=POSView.payment_amount,
                    on_change=POSView.validate_reverse,
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            rx.hstack(
                rx.dialog.close(
                    rx.button(
                        rx.icon("save", size=22),
                        type="submit",
                        disabled=POSView.is_payment_invalid,
                        background_color="#3E2723",
                        size="2",
                        variant="solid",
                    )
                ),
                rx.cond(
                    POSView.is_payment_invalid,
                    rx.text(f"{POSView.payment_error}", color="white"),
                    rx.text(""),
                ),
                spacing="2",
            ),
        ),
        on_submit=POSView.process_reverse,
        style={"width": "100%", "gap": "3", "padding": "3"},
        align="center",
        justify="center",
    )

def payment_dialog_component(order_id: int, total_paid: int, pending: int, total_order: int) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("hand-coins", size=22),
                background_color="#3E2723",
                size="2",
                variant="solid",
                title="Realizar Pago",
                on_click=POSView.set_payment_context(pending),
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title("Realizar pago"),
                update_payment_form(order_id, total_paid, pending, total_order),
                direction="column",
                align="center",
                justify="center",
                gap="3",
            ),
            background_color="#A67B5B",
        ),
        style={"width": "300px"},
    )

def reverse_dialog_component(order_id: int, total_paid: int, pending: int, total_order: int) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("undo", size=22),
                background_color="#3E2723",
                size="2",
                variant="solid",
                title="Reversar pago",
                on_click=POSView.set_reverse_context(order_id, total_paid),
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title("Reversar pago"),
                update_reverse_form(order_id, total_paid, pending, total_order),
                direction="column",
                align="center",
                justify="center",
                gap="3",
            ),
            background_color="#A67B5B",
        ),
        style={"width": "300px"},
    )

@rx.page(on_load=POSView.load_date)
def pos_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            rx.hstack(
                rx.cond(
                    POSView.is_open,
                    rx.hstack(
                        rx.input(
                            placeholder="Buscar Pedido",
                            value=POSView.pos_search,
                            on_change=POSView.on_pos_search,
                            background_color="#3E2723",
                            color="white",
                            width="200px",
                        ),
                        open_bills_modal(),
                        open_pos_modal(),
                        rx.hstack(
                            rx.checkbox(
                                checked=POSView.show_paid,
                                on_change=POSView.toggle_show_paid,
                            ),
                            rx.text("Ver Pagados", color="#3E2723"),
                            spacing="1",
                            align="center",
                        ),
                        spacing="4",
                        align="center",
                    ),
                    open_pos_modal(),
                ),
                justify="center",
                align="center",
            ),
            rx.divider(color_scheme="brown"),
            view_order_modal(),
            rx.cond(
                POSView.is_open,
                rx.vstack(
                    rx.table.root(
                        rx.table.header(get_table_header()),
                        rx.table.body(
                            rx.foreach(
                                POSView.pos_page_data,
                                lambda item, index: render_row(item),
                            )
                        ),
                        width="80vw",
                        background_color="#FFF8E1",
                        border_radius="20px",
                    ),
                    rx.hstack(
                        rx.button(
                            rx.icon("arrow-left", size=22),
                            on_click=POSView.pos_prev_page,
                            is_disabled=POSView.offset_pos <= 0,
                            background_color="#3E2723",
                            size="2",
                            variant="solid",
                        ),
                        rx.text(
                            POSView.current_page_pos,
                            " de ",
                            POSView.num_total_pages_pos,
                        ),
                        rx.button(
                            rx.icon("arrow-right", size=22),
                            on_click=POSView.pos_next_page,
                            is_disabled=POSView.offset_pos + POSView.limit_pos >= POSView.total_items_pos,
                            background_color="#3E2723",
                            size="2",
                            variant="solid",
                        ),
                        justify="center",
                        color="#3E2723",
                    ),
                    spacing="5",
                    align="center",
                ),
                rx.text(
                    "-- La caja no está abierta --",
                    size="7",
                    weight="bold",
                    color="#3E2723",
                ),
            ),

            spacing="5",
            align="center",
        ),
        display="flex",
        justify_content="center",
        align_items="flex-start",
        text_align="center",
        background_color="#FDEFEA",
        width="92vw",
        height="80vh",
    )