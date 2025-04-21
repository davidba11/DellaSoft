import reflex as rx

from rxconfig import config

from ..services.SystemService import get_sys_date_two, get_sys_date_to_string_two
from .. services.POSService import POS_is_open

class POSView(rx.State):
    sys_date: str
    is_open: bool = False

    @rx.event
    def load_date(self):
        self.sys_date = get_sys_date_to_string_two()
        record = POS_is_open(get_sys_date_two(self.sys_date))
        self.is_open = record is not None
        self.set()

def get_title():
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
            # Nombre y Categoría
            rx.grid(
                rx.text("Monto Inicial:", color="white"),
                rx.input(
                    placeholder="Monto Inicial",
                    name="initial_amount",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                    type="number"
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            # Precio
            rx.grid(
                rx.text("Monto Final:", color="white"),
                rx.input(
                    placeholder="Monto Final",
                    name="price",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                    type="number",
                    read_only=True
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            # Descripción
            rx.grid(
                rx.text("Estado:", color="white"),
                rx.select(
                    ["CERRADO", "ABIERTO"],
                    value="CERRADO",
                    #on_change=ProductView.change_value,
                    name="product_type",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    read_only=True
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),

            rx.grid(
                rx.text("Fecha:", color="white"),
                rx.input(
                    value=POSView.sys_date,
                    placeholder="Monto Final",
                    name="price",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                    read_only=True
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            # Botón Guardar
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
            spacing="3",
        ),
        #on_submit=ProductView.insert_product_controller,
        style={"width": "100%", "gap": "3", "padding": "3"},
        debug=True,
        align="center",
        justify="center",
    )

def open_pos_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.cond(
                    POSView.is_open,
                    rx.text("Ver Caja"),
                    rx.text("Abrir Caja")
                ),
                background_color="#3E2723",
                size="2",
                variant="solid",
                #on_click=POSView.load_date
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Abrir Caja'),
                create_pos_form(),  # Formulario de creación de producto
                justify='center',
                align='center',
                direction='column',
                weight="bold"
            ),
            background_color="#A67B5B",
        ),
        style={"width": "300px"}
    )

@rx.page(on_load=POSView.load_date)
def pos_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            open_pos_modal(),
            rx.divider(
                color_scheme="brown"
            ),
            rx.cond(
                POSView.is_open,
                rx.text(
                    "-- La caja está abierta --",
                    size="7",
                    weight="bold",
                    color="#3E2723",
                    high_contrast=True,
                    fontFamily="DejaVu Sans Mono",
                    width="80%"
                ),
                rx.text(
                    "-- La caja no está abierta --",
                    size="7",
                    weight="bold",
                    color="#3E2723",
                    high_contrast=True,
                    fontFamily="DejaVu Sans Mono",
                    width="80%"
                ),
            ),
            spacing="5",  # Espaciado entre elementos
            align="center",
            width="80vw",
        ),
        display="flex",
        justifyContent="center",
        alignItems="flex-start",
        text_align="center",
        background_color="#FDEFEA",
        width="92vw",
        height="80vh"
    )