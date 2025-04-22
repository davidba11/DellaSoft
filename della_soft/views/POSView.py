# POSView.py
from typing import Optional
import reflex as rx

from rxconfig import config

from ..services.SystemService import get_sys_date_two, get_sys_date_to_string_two, get_sys_date_three
from ..services.POSService import POS_is_open, insert_pos_register
from ..models.POSModel import POS

class POSView(rx.State):
    sys_date: str
    is_open: bool = False
    final_amount: float = 0.0
    pos: Optional[POS] = None

    @rx.event
    def load_date(self):
        # Carga la fecha del sistema y verifica si la caja está abierta
        self.sys_date = get_sys_date_to_string_two()
        self.pos = POS_is_open(get_sys_date_two(self.sys_date))
        self.is_open = self.pos is not None
        self.set()

    @rx.var
    def get_initial_amount(self) -> int:
        return self.pos.initial_amount
    
    @rx.var
    def get_final_amount(self) -> int:
        return self.pos.final_amount
    
    @rx.var
    def get_earnings(self) -> int:
        return (self.pos.final_amount - self.pos.initial_amount)

    @rx.event
    def on_initial_amount_change(self, value: str):
        # Actualiza final_amount cada vez que cambia el monto inicial
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
        form_data['pos_date'] = get_sys_date_three(form_data['pos_date'])
        try:
            new_pos = insert_pos_register(id="", initial_amount=form_data['initial_amount'], final_amount=form_data['final_amount'], pos_date=form_data['pos_date'])
            self.load_date()
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


@rx.page(on_load=POSView.load_date)
def pos_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            open_pos_modal(),
            rx.divider(color_scheme="brown"),
            rx.cond(
                POSView.is_open,
                rx.text(
                    "-- La caja está abierta --",
                    size="7",
                    weight="bold",
                    color="#3E2723",
                    high_contrast=True,
                    fontFamily="DejaVu Sans Mono",
                    width="80%",
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
