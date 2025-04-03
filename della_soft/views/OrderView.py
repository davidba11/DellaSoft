import reflex as rx

from typing import Any, List

from della_soft.repositories.OrderRepository import insert_order

from ..services.OrderService import select_all_order_service, select_order, create_order
from della_soft.services.CustomerService import get_customer_id_by_name_service
from ..repositories.CustomerRepository import select_by_name
from ..services.SystemService import get_sys_date_to_string

#from .OrderDetailView import OrderDetailView, OrderDetails
#from .OrderDetailView import product_order_pages

from datetime import datetime

from ..models.OrderModel import Order

class OrderView(rx.State):

    data: List[dict] = []
    columns: List[str] = ["Cliente","Observación", "Total Pedido", "Total Pagado" ,"Fecha de Ingreso", "Fecha de Entrega", "Acciones"]
    new_order: dict = {}

    sys_date: str

    input_search: str

    offset: int = 0
    limit: int = 5  # Número de pedidos por página
    total_items: int = 0  # Total de pedidos

    async def get_all_orders(self):
        orders = await select_all_order_service()  # Obtiene la lista de objetos Order
        orders_with_names = []
        for order in orders:
            orders_with_names.append({
                "id": order.id,
                "id_customer": order.id_customer,
                "customer_name": await get_customer_id_by_name_service(order.id_customer),  # Llamar async correctamente
                "observation": order.observation,
                "total_order": order.total_order,
                "total_paid": order.total_paid,
                "order_date": order.order_date.strftime('%Y-%m-%d %H:%M:%S'),  # Formateo de fecha
                "delivery_date": order.delivery_date.strftime('%Y-%m-%d %H:%M:%S')
            })
        self.total_items = len(orders_with_names)
        orders_with_names = orders_with_names[self.offset: self.offset + self.limit]
        return orders_with_names

        #return orders_with_names  # Devuelve la lista de diccionarios en lugar de objetos Order

    @rx.event
    async def load_orders(self):
        self.data = await self.get_all_orders()
        self.set()

    async def next_page(self):
        """Pasa a la siguiente página si hay más productos."""
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            await self.get_all_orders()

    async def prev_page(self):
        """Vuelve a la página anterior."""
        if self.offset > 0:
            self.offset -= self.limit
            await self.get_all_orders()

    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items + self.limit - 1) // self.limit, 1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1
    
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    async def get_order(self):
        orders = await select_order(self.input_search)
        self.data = [
            {
            "id": order.id,
            "id_customer": order.id_customer,
            "customer_name": get_customer_id_by_name_service(order.id_customer),
            "observation": order.observation,
            "total_order": order.total_order,
            "total_paid": order.total_paid,
            "order_date": order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
            "delivery_date": order.delivery_date.strftime('%Y-%m-%d %H:%M:%S')
        }
            for order in orders
        ]
        self.total_items = len(self.data)
        self.offset = 0
        self.data = self.data[self.offset: self.offset + self.limit]
        self.set()

    async def load_order_information(self, value: str):
        self.input_search = value.strip()
        await self.get_order()

    @rx.event
    def insert_order_controller(customer_name: str, observation: str, total_order: float, total_paid: float, order_date: datetime, delivery_date: datetime):
        try:
        # Buscar el id_customer usando el nombre del cliente
            customer_id = get_customer_id_by_name_service(customer_name)

        # Crear el pedido con el id_customer encontrado
            order_save = Order(
                id=None,  # Si la base de datos maneja auto increment en el ID, déjalo como None
                id_customer=customer_id,
                observation=observation,
                total_order=total_order,
                total_paid=total_paid,
                order_date=order_date,
                delivery_date=delivery_date
            )
            return insert_order(order_save)
        except ValueError as e:
            print(f"Error: {e}")
        return None  # Retorna None si no se encuentra el cliente

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
                rx.input(placeholder='Cliente', name='customer_name', width="100%"),
                rx.text_area(placeholder='Observación', description='observation', name='observation'),
            ),
            rx.hstack(
                rx.input(placeholder='Total Pedido', name='total_order', width="100%"),
                rx.input(placeholder='Total Pagado', name='total_paid', width="100%"),
            ),
            rx.hstack(
                rx.input(
                    #value=OrderView.sys_date,
                    placeholder='Fecha de Ingreso',
                    name='order_date',
                    width="100%",
                    #disabled=True,
                    type='datetime-local',
                ),
                rx.input(placeholder='Fecha de Entrega', name='delivery_date', width="100%", type='datetime-local'),
            ),
            rx.divider(),
            rx.hstack(
                #product_order_page(),
            ),
            rx.dialog.close(
                rx.button(
                    rx.icon("save", size=22),
                    type='submit',
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
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
                rx.icon("plus", size=22),
                rx.text("Crear", size="3"),
                background_color="#3E2723",
                size="2",
                variant="solid",
                on_click=lambda: OrderView.get_system_date
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
            style={"max_width": "900px", "max_height": "600px", "justify" : "center", "align" : "center"}
        ),
        style={"max_width": "900px", "max_height": "300px"}
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
        rx.table.column_header_cell(OrderView.columns[4]),
        rx.table.column_header_cell(OrderView.columns[5]),
        rx.table.column_header_cell(OrderView.columns[6]),
        color="#3E2723",
        background_color="#A67B5B",
    ),

def get_table_body(order: dict):
    return rx.table.row(
        rx.table.cell(rx.text(order["customer_name"])),
        rx.table.cell(order.observation),
        rx.table.cell(order.total_order),
        rx.table.cell(order.total_paid),
        rx.table.cell(order.order_date),
        rx.table.cell(order.delivery_date),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("eye", size=22),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    disabled=True,
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
            pagination_controls(),
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

def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("arrow-left", size=22),
            on_click=OrderView.prev_page,
            is_disabled=OrderView.offset <= 0,
            background_color="#3E2723",
            size="2",
            variant="solid"

        ),
        rx.text(  
            OrderView.current_page, " de ", OrderView.num_total_pages
        ),
        rx.button(
            rx.icon("arrow-right", size=22),
            on_click=OrderView.next_page,
            is_disabled=OrderView.offset + OrderView.limit >= OrderView.total_items,
            background_color="#3E2723",
            size="2",
            variant="solid"
        ),
        justify="center",
        color="#3E2723",
    )