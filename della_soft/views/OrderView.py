import reflex as rx
from typing import Any, List
from datetime import datetime

from ..services.OrderService import select_all_order_service, select_order, create_order
from ..services.CustomerService import select_name_by_id
from ..services.SystemService import get_sys_date_to_string, get_sys_date
from .OrderDetailView import OrderDetailView, OrderDetails
from ..models.OrderModel import Order


class OrderView(rx.State):
    data: list[dict]
    columns: List[str] = [
        "Cliente",
        "Observación",
        "Total Pedido",
        "Total Pagado",
        "Fecha de Ingreso",
        "Fecha de Entrega",
        "Acciones",
    ]
    new_order: dict = {}

    sys_date: str = ""
    input_search: str = ""

    async def get_all_orders(self):
        orders = await select_all_order_service()  # Lista de objetos Order
        orders_with_names = []
        for order in orders:
            orders_with_names.append({
                "id": order.id,
                "id_customer": order.id_customer,
                "customer_name": select_name_by_id(order.id_customer),
                "observation": order.observation,
                "total_order": order.total_order,
                "total_paid": order.total_paid,
                "order_date": order.order_date,
                "delivery_date": order.delivery_date,
            })
        return orders_with_names

    @rx.event
    async def load_orders(self):
        self.data = await self.get_all_orders()
        yield
        self.set()

    def get_order(self):
        self.data = select_order(self.input_search)

    def load_order_information(self, value: str):
        self.input_search = value

    @rx.event
    async def insert_order_controller(self, form_data: dict):
        try:
            form_data['order_date'] = get_sys_date(form_data['order_date'])
            new_order = create_order(
                id="",
                id_customer=form_data['id_customer'],
                observation=form_data['observation'],
                total_order=form_data['total_order'],
                total_paid=form_data['total_paid'],
                order_date=form_data['order_date'],
                delivery_date=form_data['delivery_date']
            )
            yield OrderView.load_orders()
            self.set()
        except BaseException as e:
            print(e.args)

    def get_system_date(self):
        self.sys_date = get_sys_date_to_string()


def get_title():
    return rx.text(
        "Pedidos",
        size="7",
        weight="bold",
        color="#3E2723",
        high_contrast=True,
        fontFamily="DejaVu Sans Mono",
        width="100%",
        text_align="center",
    ),


def search_order_component() -> rx.Component:
    return rx.hstack(
        rx.input(
            placeholder='Buscar Orden',
            background_color="#3E2723",
            on_change=OrderView.load_order_information,
            width="80%",
        ),
        rx.button(
            rx.icon("search", size=22),
            rx.text("Buscar", size="3"),
            background_color="#3E2723",
            size="2",
            variant="solid",
            on_click=OrderView.get_order,
        ),
        justify="center",
        spacing="2",
    )


def create_order_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.text("Crear Pedido", size="5", weight="bold", color="white", text_align="center"),
            rx.grid(
                rx.text("Cliente:"),
                rx.input(
                    placeholder="Cliente",
                    name="id_customer",
                    background_color="#5D4037",
                    color="white"
                ),
                rx.text("Observación:"),
                rx.text_area(
                    placeholder="Observación",
                    name="observation",
                    background_color="#5D4037",
                    color="white",
                    rows="2"
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Total Pedido:"),
                rx.input(
                    placeholder="Total Pedido",
                    name="total_order",
                    background_color="#5D4037",
                    color="white"
                ),
                rx.text("Total Pagado:"),
                rx.input(
                    placeholder="Total Pagado",
                    name="total_paid",
                    background_color="#5D4037",
                    color="white"
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Fecha de Ingreso:"),
                rx.input(
                    value=OrderView.sys_date,
                    name="order_date",
                    read_only=True,
                    background_color="#5D4037",
                    color="white"
                ),
                rx.text("Fecha de Entrega:"),
                rx.input(
                    placeholder="dd/mm/aaaa --:--",
                    name="delivery_date",
                    type="datetime-local",
                    background_color="#5D4037",
                    color="white"
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(),
            OrderDetails(),
            rx.dialog.close(
                rx.button(
                    rx.icon("save", size=22),
                    "Guardar",
                    type="submit",
                    background_color="#3E2723",
                    size="2",
                    variant="solid"
                )
            ),
            spacing="3",
        ),
        on_submit=OrderView.insert_order_controller,
        style={"width": "100%", "gap": "3", "padding": "3"},
        debug=True,
        align="center",
        justify="center",
    )


def create_order_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=22),
                rx.text("Crear", size="3"),
                background_color="#3E2723",
                size="2",
                variant="solid",
                on_click=OrderView.get_system_date,
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Crear Pedido'),
                create_order_form(),
                direction="column",
                align="center",
                justify="center",
                gap="3",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button('Cancelar', color_scheme='gray', variant='soft')
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            background_color="#A67B5B",
            style={"max_width": "900px", "max_height": "600px"},
            padding="3",
        ),
        style={"max_width": "900px", "max_height": "300px", "margin": "auto"},
    )


def main_actions_form():
    return rx.hstack(
        search_order_component(),
        create_order_modal(),
        justify="center",
        style={"margin-top": "auto", "width": "100%"},
        gap="3",
    ),


def get_table_header():
    return rx.table.row(
        rx.table.column_header_cell(OrderView.columns[0]),
        rx.table.column_header_cell(OrderView.columns[1]),
        rx.table.column_header_cell(OrderView.columns[2]),
        rx.table.column_header_cell(OrderView.columns[3]),
        rx.table.column_header_cell(OrderView.columns[4]),
        rx.table.column_header_cell(OrderView.columns[5]),
        rx.table.column_header_cell(OrderView.columns[6]),
        color="#3E2723",
        background_color="#A67B5B",
    )


def get_table_body(order: dict):
    return rx.table.row(
        rx.table.cell(rx.text(order["customer_name"], text_align="center")),
        rx.table.cell(rx.text(order["observation"], text_align="center")),
        rx.table.cell(rx.text(order["total_order"], text_align="center")),
        rx.table.cell(rx.text(order["total_paid"], text_align="center")),
        rx.table.cell(rx.text(order["order_date"], text_align="center")),
        rx.table.cell(rx.text(order["delivery_date"], text_align="center")),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("eye", size=22),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    disabled=True,
                ),
                justify="center",
            )
        ),
        color="#3E2723",
    )


@rx.page(on_load=OrderView.load_orders)
def orders() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            main_actions_form(),
            # Reemplazamos width="100%" por "80vw" para que la tabla no se expanda tanto.
            rx.table.root(
                rx.table.header(get_table_header()),
                rx.table.body(rx.foreach(OrderView.data, get_table_body)),
                width="80vw",
                background_color="#FFF8E1",
                border_radius="20px",
            ),
            spacing="5",
            align="center",
            width="80vw",          # Mismo patrón que ProductView
        ),
        display="flex",
        justifyContent="center",
        alignItems="flex-start",
        text_align="center",
        background_color="#FDEFEA",
        width="92vw",           # Mismo patrón que ProductView
        height="80vh",
    )