import reflex as rx
from typing import Optional, List

from rxconfig import config

from ..services.SystemService import (
    get_sys_date_two,
    get_sys_date_to_string_two,
    get_sys_date_three,
)
from ..services.POSService import POS_is_open, insert_pos_register
from ..services.OrderService import select_all_order_service
from ..services.CustomerService import select_name_by_id
from ..models.POSModel import POS

from .OrderView import OrderView, view_order_modal


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


def get_table_body_pos(order: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(order["id"])),
        rx.table.cell(rx.text(order["customer_name"])),
        rx.table.cell(
            rx.cond(
                order["total_paid"] == order["total_order"],
                rx.text("PAGADO"),
                rx.text("FALTA PAGO"),
            )
        ),
        rx.table.cell(rx.text(order["pending"])),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("eye", size=22),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    on_click=lambda: OrderView.open_view_modal(order["id"]),
                ),
                rx.cond(
                    order["total_paid"] == order["total_order"],
                    rx.cond(
                        OrderView.pdf_url != "",
                        rx.link(
                            rx.icon("file-text", size=22),
                            href=OrderView.pdf_url,
                            target="_blank",
                            on_click=lambda: OrderView.set_pdf_url(""),
                        ),
                        rx.button(
                            rx.icon("file-text", size=22),
                            on_click=lambda: OrderView.generate_invoice_pdf_event(order["id"]),
                            background_color="#3E2723",
                            size="2",
                            variant="solid",
                        ),
                    ),
                    payment_dialog_component(order),
                ),
                spacing="2",
            )
        ),
        color="#3E2723",
    )


class POSView(rx.State):
    sys_date: str
    is_open: bool = False
    final_amount: float = 0.0
    pos: Optional[POS] = None

    # búsqueda local y paginación
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
    def set_payment_context(self, order_id: int, pending: int):
        """Se llama al abrir el modal para fijar el límite de pago."""
        self.payment_amount = pending
        self.max_payment = pending
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
    def on_pos_search(self, value: str):
        q = (value or "").strip().lower()
        self.pos_search = q
        # reset paginado al buscar
        self.offset_pos = 0
        if not q:
            self.filtered_pos_data = self.pos_data
        else:
            resultados = []
            for o in self.pos_data:
                estado = "pagado" if o["total_paid"] == o["total_order"] else "falta pago"
                pending = str(o["pending"])
                if (
                    q in str(o["id"]).lower()
                    or q in o["customer_name"].lower()
                    or q in estado
                    or q in pending
                ):
                    resultados.append(o)
            self.filtered_pos_data = resultados
        self.total_items_pos = len(self.filtered_pos_data)
        self.set()

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

        # cargar pedidos
        orders = await select_all_order_service()
        data = []
        for o in orders:
            data.append({
                "id": o.id,
                "customer_name": select_name_by_id(o.id_customer),
                "total_order": o.total_order,
                "total_paid": o.total_paid,
                "pending": o.total_order - o.total_paid,
            })
        self.pos_data = data
        self.filtered_pos_data = data
        self.total_items_pos = len(data)
        self.offset_pos = 0
        self.set()

    @rx.var
    def get_initial_amount(self) -> int:
        return self.pos.initial_amount

    @rx.var
    def get_final_amount(self) -> int:
        return self.pos.final_amount

    @rx.var
    def get_earnings(self) -> int:
        return self.pos.final_amount - self.pos.initial_amount

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
            # Monto Inicial
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
            # Estado de la caja
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
            # Fecha del sistema
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
            # Botón de cierre del modal
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
                # Botón Guardar si está cerrada
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
        debug=True,
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

# 2) Función completa update_payment_form con el aviso junto al botón:

def update_payment_form(order: dict) -> rx.Component:
    return rx.form(
        rx.vstack(
            # --- Grid de campos de solo lectura + editable ---
            rx.grid(
                rx.text("Monto Pagado:", color="white"),
                rx.input(
                    name="total_paid",
                    type="number",
                    default_value=order["total_paid"],
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                    read_only=True,
                ),
                rx.text("Monto Faltante:", color="white"),
                rx.input(
                    name="pending_amount",
                    type="number",
                    default_value=order["pending"],
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                    read_only=True,
                ),
                rx.text("Monto Total:", color="white"),
                rx.input(
                    name="total_order",
                    type="number",
                    default_value=order["total_order"],
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                    read_only=True,
                ),
                rx.text("Monto a Pagar:", color="white"),
                rx.input(
                    name="pending",
                    type="number",
                    default_value=order["pending"],
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                    on_change=POSView.validate_payment,
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),

            rx.divider(color="white"),

            # --- Botón + mensaje de error al lado ---
            rx.hstack(
                rx.dialog.close(
                    rx.cond(
                        POSView.is_payment_invalid,
                        # botón deshabilitado
                        rx.button(
                            rx.icon("save", size=22),
                            type="submit",
                            background_color="#3E2723",
                            size="2",
                            variant="solid",
                            disabled=True,
                        ),
                        # botón habilitado
                        rx.button(
                            rx.icon("save", size=22),
                            type="submit",
                            background_color="#3E2723",
                            size="2",
                            variant="solid",
                            disabled=False,
                        ),
                    )
                ),
                # Texto de error con símbolo de alerta
                rx.cond(
                    POSView.is_payment_invalid,
                    rx.text(f"⚠️ {POSView.payment_error}", color="white"),
                    rx.text(""),  # nada si es válido
                ),
                spacing="2",
            ),

            spacing="3",
        ),
        # on_submit=POSView.process_payment,  # reactívalo cuando implementes el handler
        style={"width": "100%", "gap": "3", "padding": "3"},
        align="center",
        justify="center",
        debug=True,
    )


def payment_dialog_component(order: dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("hand-coins", size=22),
                background_color="#3E2723",
                size="2",
                variant="solid",
                on_click=lambda: POSView.set_payment_context(order["id"], order["pending"]),
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title("Realizar pago"),
                update_payment_form(order),
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
            open_pos_modal(),
            rx.divider(color_scheme="brown"),
            rx.cond(
                POSView.is_open,
                rx.vstack(
                    rx.hstack(
                        rx.input(
                            name="pos_search",
                            value=POSView.pos_search,
                            placeholder="Buscar Pedido",
                            background_color="#3E2723",
                            color="white",
                            on_change=POSView.on_pos_search,
                            width="80%",
                        ),
                        justify="center",
                        gap="3",
                    ),
                    view_order_modal(),
                    rx.table.root(
                        rx.table.header(get_table_header()),
                        rx.table.body(rx.foreach(POSView.pos_page_data, get_table_body_pos)),
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
                        rx.text(POSView.current_page_pos, " de ", POSView.num_total_pages_pos),
                        rx.button(
                            rx.icon("arrow-right", size=22),
                            on_click=POSView.pos_next_page,
                            is_disabled=(POSView.offset_pos + POSView.limit_pos >= POSView.total_items_pos),
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
                    high_contrast=True,
                    fontFamily="DejaVu Sans Mono",
                    width="80%",
                ),
            ),
            spacing="5",
            align="center",
            width="80vw",
        ),
        display="flex",
        justify_content="center",
        align_items="flex-start",
        text_align="center",
        background_color="#FDEFEA",
        width="92vw",
        height="80vh",
    )
