import asyncio

import reflex as rx

from rxconfig import config

from typing import Any, List

from ..services.OrderService import select_all_order_service, select_order, create_order
from ..services.CustomerService import select_name_by_id

from ..models.OrderModel import Order

class OrderView(rx.State):

    data: list[Order]
    columns: List[str] = ["Cliente", "Fecha de Ingreso", "Fecha de Entrega", "Acciones"]
    new_order: dict = {}

    input_search: str

    async def get_all_orders(self):
        data = await select_all_order_service()
        return data

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
            new_order = create_order(id="", id_customer=form_data['id_customer'], observation=form_data['observation'], total_order=form_data['total_order'], total_paid=form_data['total_paid'], order_date=form_data['order_date'], delivery_date=form_data['delivery_date'])
            yield OrderView.load_orders()
            self.set()
        except BaseException as e:
            print(e.args)

def get_name(id_customer: int):
    print(id_customer)
    try:
        print(id_customer)
        return select_name_by_id(int(id_customer))
    except (ValueError, TypeError):
        return "ID inválido"

def get_title():
    return rx.text(
        "Pedidos",
        size="7",
        weight="bold",
        color="#3E2723",
        high_contrast=True,
        fontFamily="DejaVu Sans Mono",
        width="80%",
    ),

def search_order_component () ->rx.Component:
    return rx.hstack(
        rx.input(
            placeholder='Buscar Orden',
            background_color="#3E2723",
            on_change=OrderView.load_order_information,
        ),
        rx.button(
            rx.icon("search", size=22),
            rx.text("Buscar", size="3"),
            background_color="#3E2723",
            size="2",
            variant="solid",
            on_click=lambda: OrderView.get_order,
        ),
    )

def create_order_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.hstack(
                rx.input(placeholder='Cliente', name='id_customer', width="100%"),
                rx.text_area(placeholder='Observación', description='observation', name='observation'),
            ),
            rx.hstack(
                rx.input(placeholder='Total Pedido', name='total_order', width="100%"),
                rx.input(placeholder='Total Pagado', name='total_paid', width="100%"),
            ),
            rx.hstack(
                rx.input(placeholder='Fecha de Ingreso', name='order_date', width="100%"),
                rx.input(placeholder='Fecha de Entrega', name='delivery_date', width="100%"),
            ),
            rx.dialog.close(
                rx.button(
                    'Guardar',
                    type='submit',
                ),
            ),   
        ),
        on_submit=lambda form_data: OrderView.insert_order_controller(form_data),
        debug=True,
    )

def create_order_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("cake", size=22),
                rx.text("Crear", size="3"),
                background_color="#3E2723",
                size="2",
                variant="solid",
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Crear Pedido'),
                create_order_form(),
                justify='center',
                align='center',
                direction='column',
                weight="bold",
                color="#3E2723"
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
        ),
        style={"width": "300px"}
    )

def main_actions_form():
    return rx.hstack(
        search_order_component(), 
        create_order_modal(),
        justify='center',
        style={"margin-top": "auto"}
    ),

def get_table_header():
    return rx.table.row(
        rx.table.column_header_cell(OrderView.columns[0]),
        rx.table.column_header_cell(OrderView.columns[1]),
        rx.table.column_header_cell(OrderView.columns[2]),
        rx.table.column_header_cell(OrderView.columns[3]),
        color="#3E2723",
        background_color="#A67B5B",
    ),

def get_table_body(order: Order):
    customer_name = get_name(order.id_customer)
    return rx.table.row(
        rx.table.cell(customer_name),
        rx.table.cell(order.order_date),
        rx.table.cell(order.delivery_date),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("eye", size=22),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    #on_click=OrderView.view_order_detail(order.id)
                ),
            ),
        ),
        color="#3E2723",
    )

@rx.page(on_load=OrderView.load_orders)
def orders() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            main_actions_form(),
            rx.table.root(
                rx.table.header(
                    get_table_header(),
                ),
                rx.table.body(
                    rx.foreach(OrderView.data, get_table_body)
                ),
                width="80vw",
                background_color="#FFF8E1",
                border_radius="20px",
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
        height="80vh",
    )