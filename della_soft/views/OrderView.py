# OrderView.py
import reflex as rx
from typing import List

from ..models.ProductOrderModel import ProductOrder
from ..repositories.ProductOrderRepository import insert_product_order
from ..services.ProductOrderService import insert_product_order_service
from ..repositories.OrderRepository import insert_order
from ..services.OrderService import select_all_order_service, select_order
from ..services.CustomerService import select_name_by_id, select_all_customer_service
from ..services.SystemService import get_sys_date_to_string, get_sys_date

from .OrderDetailView import OrderDetailView, OrderDetails
from ..models.OrderModel import Order

class OrderView(rx.State):
    # Tabla de pedidos
    data: List[dict] = []
    columns: List[str] = [
        "Cliente", "Observación", "Total Pedido", "Total Pagado",
        "Fecha de Ingreso", "Fecha de Entrega", "Acciones"
    ]

    # Autocomplete clientes
    customer_options: List[str] = []
    _customer_map: dict[str, str] = {}
    customer_search: str = ""
    customer_dropdown_open: bool = False
    selected_customer_label: str = ""

    sys_date: str
    input_search: str

    # Paginación
    offset: int = 0
    limit: int = 5
    total_items: int = 0

    @rx.event
    async def load_customers(self):
        customers = await select_all_customer_service()
        opts, cmap = [], {}
        for c in customers:
            label = f"({c.ci or 0}) {c.first_name} {c.last_name}"
            opts.append(label)
            cmap[label] = str(c.id)
        self.customer_options = opts
        self._customer_map = cmap
        self.customer_search = ""
        self.selected_customer_label = ""
        self.customer_dropdown_open = False
        self.set()

    @rx.event
    def on_customer_search(self, value: str):
        self.customer_search = value or ""
        self.customer_dropdown_open = True
        self.set()

    @rx.var
    def filtered_customer_options(self) -> List[str]:
        if not self.customer_search:
            return self.customer_options
        txt = self.customer_search.lower()
        return [opt for opt in self.customer_options if txt in opt.lower()]

    @rx.event
    def select_customer(self, label: str):
        self.selected_customer_label = label
        self.customer_search = label
        self.customer_dropdown_open = False
        self.set()

    async def get_all_orders(self):
        orders = await select_all_order_service()
        lst = []
        for o in orders:
            lst.append({
                "id": o.id,
                "id_customer": o.id_customer,
                "customer_name": select_name_by_id(o.id_customer),
                "observation": o.observation,
                "total_order": o.total_order,
                "total_paid": o.total_paid,
                "order_date": o.order_date.strftime('%Y-%m-%d %H:%M:%S') if o.order_date else "",
                "delivery_date": o.delivery_date.strftime('%Y-%m-%d %H:%M:%S') if o.delivery_date else ""
            })
        self.total_items = len(lst)
        return lst[self.offset : self.offset + self.limit]

    @rx.event
    async def load_orders(self):
        self.data = await self.get_all_orders()
        self.set()

    async def next_page(self):
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            self.data = await self.get_all_orders()
            self.set()

    async def prev_page(self):
        if self.offset > 0:
            self.offset -= self.limit
            self.data = await self.get_all_orders()
            self.set()

    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items + self.limit - 1) // self.limit, 1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1

    async def get_order(self):
        orders = await select_order(self.input_search)
        self.data = [{
            "id": o.id,
            "id_customer": o.id_customer,
            "customer_name": select_name_by_id(o.id_customer),
            "observation": o.observation,
            "total_order": o.total_order,
            "total_paid": o.total_paid,
            "order_date": o.order_date.strftime('%Y-%m-%d %H:%M:%S') if o.order_date else "",
            "delivery_date": o.delivery_date.strftime('%Y-%m-%d %H:%M:%S') if o.delivery_date else ""
        } for o in orders]
        self.total_items = len(self.data)
        self.offset = 0
        self.data = self.data[: self.limit]
        self.set()

    async def load_order_information(self, value: str):
        self.input_search = value.strip()
        await self.get_order()

    @rx.event
    async def insert_order_controller(self, form_data: dict):
        try:
            sel = form_data.get("id_customer", "")
            form_data["id_customer"] = int(self._customer_map.get(sel, sel))
            form_data['order_date'] = get_sys_date(form_data['order_date'])
            order_save = Order(
                id=None,
                id_customer=form_data["id_customer"],
                observation=form_data["observation"],
                total_order=float(form_data["total_order"]),
                total_paid=float(form_data["total_paid"]),
                order_date=form_data["order_date"],
                delivery_date=form_data["delivery_date"],
            )
            new_order = insert_order(order_save)

            detail_state = await self.get_state(OrderDetailView)
            for prod in detail_state.plain_data:
                qty = detail_state.product_counts.get(prod.id, 0)
                if qty > 0:
                    po = ProductOrder(id=None, quantity=qty, id_product=prod.id, id_order=new_order.id)
                    insert_product_order_service(po)

            yield OrderView.load_orders()
            self.set()
        except Exception as e:
            print("Error en insert_order_controller:", e)

    def get_system_date(self):
        self.sys_date = get_sys_date_to_string()
        yield OrderDetailView.load_OrderDetails()
        yield OrderView.load_customers()


def get_title() -> rx.Component:
    return rx.text(
        "Pedidos", size="7", weight="bold", color="#3E2723",
        fontFamily="DejaVu Sans Mono", width="100%", text_align="center"
    ),


def search_order_component() -> rx.Component:
    return rx.hstack(
        rx.input(
            placeholder="Buscar Orden", color="white",
            background_color="#3E2723", on_change=OrderView.load_order_information,
            width="80%"
        ),
        justify="center", spacing="2"
    )


def create_order_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.text("Crear Pedido", size="5", weight="bold", color="white", text_align="center"),
            rx.grid(
                rx.text("Cliente:"),
                rx.vstack(
                    rx.box(
                        rx.input(
                            placeholder="Buscar Cliente...",
                            background_color="#5D4037",
                            color="white",
                            value=OrderView.customer_search,
                            on_change=OrderView.on_customer_search,
                        ),
                        rx.cond(
                            OrderView.customer_dropdown_open,
                            rx.vstack(
                                rx.foreach(
                                    OrderView.filtered_customer_options,
                                    lambda label: rx.box(
                                        rx.text(label, text_align="center", color="#3E2723"),
                                        on_click=lambda label=label: OrderView.select_customer(label),
                                        style={
                                            "padding": "0.5rem",
                                            "cursor": "pointer",
                                            "_hover": {"background_color": "#A67B5B", "color": "white"},
                                        },
                                    ),
                                ),
                                background_color="#FFF8E1",
                                border="1px solid #A67B5B",
                                border_radius="0 0 8px 8px",
                                max_height="160px",
                                overflow_y="auto",
                                style={
                                    "position": "absolute", "top": "100%",
                                    "left": 0, "right": 0, "z_index": 1000,
                                },
                            ),
                        ),
                        style={"position": "relative", "width": "100%"},
                    ),
                    rx.input(
                        name="id_customer", type="hidden",
                        value=OrderView.selected_customer_label,
                    ),
                ),
                rx.text("Observación:"),
                rx.text_area(name="observation", background_color="#5D4037", color="white", rows="3"),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            rx.grid(
                rx.text("Total Pedido:"),
                rx.input(name="total_order", value=OrderDetailView.total,
                         background_color="#5D4037", color="white", read_only=True),
                rx.text("Total Pagado:"),
                rx.input(name="total_paid", background_color="#5D4037", color="white"),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            rx.grid(
                rx.text("Fecha de Ingreso:"),
                rx.input(value=OrderView.sys_date, name="order_date",
                         read_only=True, background_color="#5D4037", color="white"),
                rx.text("Fecha de Entrega:"),
                rx.input(name="delivery_date", type="datetime-local",
                         background_color="#5D4037", color="white"),
                columns="1fr 2fr", gap="3", width="100%",
            ),
            rx.divider(),
            OrderDetails(),
            rx.dialog.close(
                rx.button(rx.icon("save", size=22), "Guardar", type="submit",
                          background_color="#3E2723", size="2", variant="solid")
            ),
            spacing="3",
        ),
        on_submit=OrderView.insert_order_controller,
        style={"width": "100%", "gap": "3", "padding": "3"},
        debug=True, align="center", justify="center",
    )


def create_order_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(rx.icon("plus", size=22), rx.text("Crear", size="3"),
                      background_color="#3E2723", size="2", variant="solid",
                      on_click=OrderView.get_system_date)
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title("Crear Pedido"),
                create_order_form(),
                direction="column", align="center", justify="center", gap="3"
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancelar", color_scheme="gray", variant="soft", type="button")
                ),
                justify="end", spacing="3", margin_top="16px"
            ),
            background_color="#A67B5B", style={"max_width": "900px", "max_height": "600px"}, padding="3"
        ),
        style={"max_width": "900px", "max_height": "300px", "margin": "auto"},
    )


def main_actions_form() -> rx.Component:
    return rx.hstack(
        search_order_component(),
        create_order_modal(),
        justify="center", style={"margin-top": "auto", "width": "100%"}, gap="3"
    ),


def get_table_header() -> rx.Component:
    return rx.table.row(
        rx.table.column_header_cell("Cliente"),
        rx.table.column_header_cell("Observación"),
        rx.table.column_header_cell("Total Pedido"),
        rx.table.column_header_cell("Total Pagado"),
        rx.table.column_header_cell("Fecha de Ingreso"),
        rx.table.column_header_cell("Fecha de Entrega"),
        rx.table.column_header_cell("Acciones"),
        color="#3E2723", background_color="#A67B5B",
    )


def get_table_body(order: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(order["customer_name"], text_align="center")),
        rx.table.cell(rx.text(order["observation"], text_align="center")),
        rx.table.cell(rx.text(order["total_order"], text_align="center")),
        rx.table.cell(rx.text(order["total_paid"], text_align="center")),
        rx.table.cell(rx.text(order["order_date"], text_align="center")),
        rx.table.cell(rx.text(order["delivery_date"], text_align="center")),
        rx.table.cell(
            rx.hstack(
                rx.button(rx.icon("eye", size=22), background_color="#3E2723", size="2", variant="solid", disabled=True),
                justify="center"
            )
        ),
        color="#3E2723",
    )


def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button(rx.icon("arrow-left", size=22), on_click=OrderView.prev_page,
                  is_disabled=OrderView.offset <= 0, background_color="#3E2723",
                  size="2", variant="solid"),
        rx.text(OrderView.current_page, " de ", OrderView.num_total_pages),
        rx.button(rx.icon("arrow-right", size=22), on_click=OrderView.next_page,
                  is_disabled=OrderView.offset + OrderView.limit >= OrderView.total_items,
                  background_color="#3E2723", size="2", variant="solid"),
        justify="center", color="#3E2723"
    )

@rx.page(on_load=OrderView.load_orders)
def orders() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            main_actions_form(),
            rx.table.root(
                rx.table.header(get_table_header()),
                rx.table.body(rx.foreach(OrderView.data, get_table_body)),
                width="80vw", background_color="#FFF8E1", border_radius="20px"
            ),
            pagination_controls(), spacing="5", align="center", width="80vw"
        ),
        display="flex", justify_content="center", align_items="flex-start",
        text_align="center", background_color="#FDEFEA",
        width="92vw", height="80vh"
    )
