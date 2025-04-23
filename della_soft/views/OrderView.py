# OrderView.py
import reflex as rx
from typing import List

from della_soft.services.ProductService import select_all_product_service
from della_soft.views.generateInvoicePDF import generate_invoice_pdf

from ..models.ProductOrderModel import ProductOrder
from ..services.ProductOrderService import (
    insert_product_order_service,
    select_by_order_id_service,
    update_product_orders,
)
from ..repositories.OrderRepository import insert_order
from ..services.OrderService import select_all_order_service, update_order_service
from ..services.CustomerService import select_name_by_id, select_all_customer_service
from ..services.SystemService import get_sys_date_to_string, get_sys_date
from ..repositories.ProductRepository import get_product

from .OrderDetailView import OrderDetailView, OrderDetails
import os
from ..models.OrderModel import Order

class OrderView(rx.State):
    # Tabla de pedidos
    data: List[dict] = []
    columns = [
        "Cliente", "Observación", "Total Pedido", "Total Pagado",
        "Fecha de Ingreso", "Fecha de Entrega", "Acciones",
    ]

    # Autocomplete clientes
    customer_options: List[str] = []
    _customer_map: dict[str, str] = {}
    customer_search = ""
    customer_dropdown_open = False
    selected_customer_label = ""

    # Modal de vista de pedido
    view_modal_open = False
    edit_modal_open = False
    modal_order: Order | None = None
    modal_customer_name = ""
    modal_order_date_str = ""
    modal_delivery_date_str = ""
    modal_order_details: List[dict] = []
    modal_total_order_str = ""
    modal_total_paid_str = ""

    @rx.var
    def modal_observation_str(self) -> str:
        if self.modal_order and self.modal_order.observation:
            return self.modal_order.observation
        return ""

    # Búsqueda y paginación
    sys_date = ""
    input_search = ""
    offset = 0
    limit = 5
    total_items = 0

    pdf_url = ""

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

    @rx.event
    async def open_view_modal(self, order_id: int):
        orders = await select_all_order_service()
        order = next((o for o in orders if o.id == order_id), None)
        if not order:
            return

        # Rellenar datos del modal
        self.modal_order = order
        self.modal_customer_name = select_name_by_id(order.id_customer)
        self.modal_order_date_str = (
            order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else ""
        )
        self.modal_delivery_date_str = (
            order.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if order.delivery_date else ""
        )
        self.modal_total_order_str = f"{order.total_order}"
        self.modal_total_paid_str = f"{order.total_paid}"

        # Sólo detalles con cantidad > 0
        details = select_by_order_id_service(order_id)
        products = await select_all_product_service()
        lst = []
        for d in details:
            if d.quantity > 0:
                prod = next((p for p in products if p.id == d.id_product), None)
                name = prod.name if prod else ""
                price = prod.price if prod else 0
                lst.append({
                    "product_name": name,
                    "quantity": d.quantity,
                    "price": price,
                    "subtotal": d.quantity * price,
                })
        self.modal_order_details = lst

        self.view_modal_open = True
        self.set()

    @rx.event
    def close_view_modal(self):
        self.view_modal_open = False
        self.set()

    async def get_all_orders(self):
        orders = await select_all_order_service()
        lst = []
        for o in orders:
            lst.append({
                "id": o.id,
                "id_customer": o.id_customer,
                "customer_name": select_name_by_id(o.id_customer),
                "observation": o.observation or "",
                "total_order": o.total_order,
                "total_paid": o.total_paid,
                "order_date": o.order_date.strftime("%Y-%m-%d %H:%M:%S") if o.order_date else "",
                "delivery_date": o.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if o.delivery_date else "",
                "pending": o.total_order - o.total_paid,
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

    @rx.event
    async def load_order_information(self, value: str):
        self.input_search = (value or "").strip()
        await self.get_order()

    async def get_order(self):
        orders = await select_all_order_service()
        q = (self.input_search or "").lower()
        resultados = []
        for o in orders:
            cliente = select_name_by_id(o.id_customer) or ""
            obs     = o.observation or ""
            fecha_o = o.order_date.strftime("%Y-%m-%d %H:%M:%S") if o.order_date else ""
            fecha_d = o.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if o.delivery_date else ""
            # calculamos el estado que mostramos en la columna ¿Pagado Totalmente?
            estado = "PAGADO" if o.total_paid == o.total_order else "FALTA PAGO"
            # armamos la lista de campos para buscar
            campos = [
                str(o.id),
                cliente,
                obs,
                f"{o.total_order}",
                f"{o.total_paid}",
                estado,            # <-- aquí lo añadimos
                fecha_o,
                fecha_d,
            ]
            # si coincide en alguno, lo añadimos a resultados
            if any(q in campo.lower() for campo in campos):
                resultados.append({
                    "id": o.id,
                    "id_customer": o.id_customer,
                    "customer_name": cliente,
                    "observation": obs,
                    "total_order": o.total_order,
                    "total_paid": o.total_paid,
                    "delivery_date": fecha_d,
                    "pending": o.total_order - o.total_paid,
                })
        self.total_items = len(resultados)
        self.offset = 0
        self.data = resultados[self.offset : self.offset + self.limit]
        self.set()


    @rx.event
    async def insert_order_controller(self, form_data: dict):
        sel = form_data.get("id_customer", "")
        form_data["id_customer"] = int(self._customer_map.get(sel, sel))
        form_data["order_date"] = get_sys_date(form_data["order_date"])
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

    @rx.event
    async def edit_order(self, order_id: int):
        orders = await select_all_order_service()
        order = next((o for o in orders if o.id == order_id), None)
        if not order:
            return

        self.modal_order = order
        self.modal_customer_name = select_name_by_id(order.id_customer)
        self.modal_order_date_str = (
            order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else ""
        )
        self.modal_delivery_date_str = (
            order.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if order.delivery_date else ""
        )
        self.modal_total_paid_str = f"{order.total_paid}"

        detail_state = await self.get_state(OrderDetailView)
        products = await select_all_product_service()
        detail_state.plain_data = products[:]
        detail_state.product_counts = {p.id: 0 for p in products}
        detail_state.total_items = len(products)
        detail_state.offset = 0
        detail_state.limit = 3
        detail_state.data = products[:detail_state.limit]

        details = select_by_order_id_service(order_id)
        for d in details:
            prod = next((p for p in products if p.id == d.id_product), None)
            if prod:
                detail_state.product_counts[prod.id] = d.quantity
        detail_state.set()

        self.edit_modal_open = True
        self.set()

    @rx.event
    async def set_edit_modal_open(self, is_open: bool):
        self.edit_modal_open = is_open
        if not is_open:
            detail_state = await self.get_state(OrderDetailView)
            detail_state.set()
        self.set()

    @rx.event
    async def generate_invoice_pdf_event(self, order_id: int):
        path = generate_invoice_pdf(order_id)
        with open(path, "rb") as f:
            pdf_bytes = f.read()
        yield rx.download(data=pdf_bytes, filename=f"factura_{order_id}.pdf")
        yield rx.toast("Factura generada con éxito")

    @rx.event
    async def update_order_controller(self, form_data: dict):
        form_data["id_customer"] = int(form_data["id_customer"])
        detail_state = await self.get_state(OrderDetailView)
        detail_state.set()

        total = 0
        new_products = []
        for p in detail_state.plain_data:
            qty = detail_state.product_counts.get(p.id, 0)
            if qty > 0:
                subtotal = p.price * qty
                total += subtotal
                new_products.append(ProductOrder(
                    id=None, quantity=qty, id_product=p.id, id_order=self.modal_order.id
                ))

        if not new_products:
            print("❌ No se seleccionaron productos válidos.")
            return

        from ..services.SystemService import get_sys_date
        form_data["delivery_date"] = get_sys_date(form_data["delivery_date"])
        form_data["total_paid"] = float(form_data.get("total_paid", 0) or 0)

        updated_order = Order(
            id=self.modal_order.id,
            id_customer=form_data["id_customer"],
            observation=form_data["observation"],
            total_order=total,
            total_paid=form_data["total_paid"],
            order_date=self.modal_order.order_date,
            delivery_date=form_data["delivery_date"],
        )

        update_order_service(updated_order)
        update_product_orders(self.modal_order.id, new_products)

        self.edit_modal_open = False
        yield rx.toast("Pedido actualizado con éxito")
        yield OrderView.load_orders()
        self.set()

    def get_system_date(self):
        self.sys_date = get_sys_date_to_string()
        yield OrderDetailView.reset_product_counts()
        yield OrderView.load_customers()


def get_title() -> rx.Component:
    return rx.text(
        "Pedidos", size="7", weight="bold", color="#3E2723",
        fontFamily="DejaVu Sans Mono", width="100%", text_align="center"
    ),


def search_order_component() -> rx.Component:
    return rx.hstack(
        rx.input(
            name="search",
            value=OrderView.input_search,
            placeholder="Buscar Pedido",
            background_color="#3E2723",
            color="white",
            on_change=OrderView.load_order_information,
            width="80%",
        ),
        justify="center",
        spacing="2",
    )


def create_order_form() -> rx.Component:
    return rx.form(
        rx.vstack(
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
                                    "position": "absolute",
                                    "top": "100%",
                                    "left": 0,
                                    "right": 0,
                                    "z_index": 1000,
                                },
                            ),
                        ),
                        style={"position": "relative", "width": "100%"},
                    ),
                    rx.input(
                        name="id_customer",
                        type="hidden",
                        value=OrderView.selected_customer_label,
                    ),
                ),
                rx.text("Observación:"),
                rx.text_area(name="observation", background_color="#5D4037", color="white", rows="3"),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Total Pedido:"),
                rx.input(
                    name="total_order",
                    value=OrderDetailView.total,
                    read_only=True,
                    background_color="#5D4037",
                    color="white",
                ),
                rx.text("Total Pagado:"),
                rx.input(name="total_paid", background_color="#5D4037", color="white"),
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
                    color="white",
                ),
                rx.text("Fecha de Entrega:"),
                rx.input(
                    name="delivery_date",
                    type="datetime-local",
                    background_color="#5D4037",
                    color="white",
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
                    type="submit",
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
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


def edit_order_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(name="id_customer", type="hidden", value=OrderView.modal_order.id_customer),
            rx.grid(
                rx.text("Cliente:"),
                rx.input(
                    value=OrderView.modal_customer_name,
                    read_only=True,
                    background_color="#5D4037",
                    color="white",
                ),
                rx.text("Observación:"),
                rx.text_area(
                    name="observation",
                    rows="3",
                    default_value=OrderView.modal_order.observation,
                    background_color="#5D4037",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Total Pedido:"),
                rx.input(
                    name="total_order",
                    value=OrderDetailView.total,
                    read_only=True,
                    background_color="#5D4037",
                    color="white",
                ),
                rx.text("Total Pagado:"),
                rx.input(
                    name="total_paid",
                    type="number",
                    default_value=OrderView.modal_total_paid_str,
                    background_color="#5D4037",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Fecha de Ingreso:"),
                rx.input(
                    name="order_date",
                    value=OrderView.modal_order_date_str,
                    read_only=True,
                    background_color="#5D4037",
                    color="white",
                ),
                rx.text("Fecha de Entrega:"),
                rx.input(
                    name="delivery_date",
                    type="datetime-local",
                    default_value=OrderView.modal_delivery_date_str.replace(" ", "T"),
                    background_color="#5D4037",
                    color="white",
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
                    "Actualizar Pedido",
                    type="submit",
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                )
            ),
            spacing="3",
        ),
        on_submit=OrderView.update_order_controller,
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
                background_color="#3E2723",
                size="2",
                variant="solid",
                on_click=OrderView.get_system_date,
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title("Crear Pedido"),
                create_order_form(),
                direction="column",
                align="center",
                justify="center",
                gap="3",
            ),
            background_color="#A67B5B",
            style={"max_width": "900px", "max_height": "600px"},
            padding="3",
        ),
        style={"max_width": "900px", "max_height": "300px", "margin": "auto"},
    )


def view_order_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.text("Detalle del Pedido", size="5", weight="bold", color="#3E2723", text_align="center"),
                rx.grid(
                    rx.text("Cliente:", weight="bold", color="#3E2723"),
                    rx.text(OrderView.modal_customer_name, color="#3E2723"),
                    rx.text("Observación:", weight="bold", color="#3E2723"),
                    rx.text(OrderView.modal_observation_str, color="#3E2723"),
                    rx.text("Total Pedido:", weight="bold", color="#3E2723"),
                    rx.text(OrderView.modal_total_order_str, color="#3E2723"),
                    rx.text("Total Pagado:", weight="bold", color="#3E2723"),
                    rx.text(OrderView.modal_total_paid_str, color= "#3E2723"),
                    rx.text("Fecha de Ingreso:", weight="bold", color= "#3E2723"),
                    rx.text(OrderView.modal_order_date_str, color= "#3E2723"),
                    rx.text("Fecha de Entrega:", weight="bold", color= "#3E2723"),
                    rx.text(OrderView.modal_delivery_date_str, color="#3E2723"),
                    columns="repeat(2,1fr)",
                    gap="2",
                    width="100%",
                    justify_items="start",
                ),
                rx.table.root(
                    rx.table.header(
                        rx.table.column_header_cell("Producto"),
                        rx.table.column_header_cell("Cantidad"),
                        rx.table.column_header_cell("Precio"),
                        rx.table.column_header_cell("Subtotal"),
                        background_color="#A67B5B",
                        color="white",
                        text_align="center",
                    ),
                    rx.table.body(
                        rx.foreach(
                            OrderView.modal_order_details,
                            lambda d: rx.table.row(
                                rx.table.cell(rx.text(d["product_name"], text_align="center")),
                                rx.table.cell(rx.text(d["quantity"], text_align="center")),
                                rx.table.cell(rx.text(d["price"], text_align="center")),
                                rx.table.cell(rx.text(d["subtotal"], text_align="center")),
                                color="#3E2723",
                            ),
                        )
                    ),
                    width="90%",
                    background_color="#FFF8E1",
                    border_radius="8px",
                    margin="auto",
                ),
                spacing="4",
                align="center",
                width="100%",
            ),
            background_color="#FDEFEA",
            padding="4",
            border_radius="8px",
            style={"max_width":"600px","margin":"auto"},
        ),
        open=OrderView.view_modal_open,
        on_open_change=OrderView.close_view_modal,
    )


def get_table_header() -> rx.Component:
    return rx.table.row(
        rx.table.column_header_cell("ID"),
        rx.table.column_header_cell("Cliente"),
        rx.table.column_header_cell("¿Pagado Totalmente?"),
        rx.table.column_header_cell("Fecha de Entrega"),
        rx.table.column_header_cell("Acciones"),
        color="#3E2723",
        background_color="#A67B5B",
    )


def get_table_body(order: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(order["id"])),
        rx.table.cell(rx.text(order["customer_name"])),
        rx.table.cell(
            rx.cond(
                order["total_paid"] == order["total_order"],
                rx.text("PAGADO"),
                rx.text("FALTA PAGO")
            )
        ),
        rx.table.cell(rx.text(order["delivery_date"])),
        rx.table.cell(
            rx.hstack(
                # Ver detalle
                rx.button(
                    rx.icon("eye", size=22),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    on_click=lambda: OrderView.open_view_modal(order["id"]),
                ),
                # Editar
                rx.button(
                    rx.icon("square-pen", size=22),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    on_click=lambda: OrderView.edit_order(order["id"]),
                ),
                # PDF
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
                spacing="2",  # <-- aquí el espacio entre botones
            )
        ),
        color="#3E2723",
    )


def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("arrow-left", size=22),
            on_click=OrderView.prev_page,
            is_disabled=OrderView.offset <= 0,
            background_color="#3E2723",
            size="2",
            variant="solid",
        ),
        rx.text(OrderView.current_page, " de ", OrderView.num_total_pages),
        rx.button(
            rx.icon("arrow-right", size=22),
            on_click=OrderView.next_page,
            is_disabled=OrderView.offset + OrderView.limit >= OrderView.total_items,
            background_color="#3E2723",
            size="2",
            variant="solid",
        ),
        justify="center",
        color="#3E2723",
    )


def edit_order_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.flex(
                rx.dialog.title("Editar Pedido"),
                edit_order_form(),
                direction="column",
                align="center",
                justify="center",
                gap="3",
            ),
            background_color="#A67B5B",
            style={"max_width":"900px","max_height":"600px"},
            padding="3",
        ),
        open=OrderView.edit_modal_open,
        on_open_change=OrderView.set_edit_modal_open,
    )


@rx.page(on_load=OrderView.load_orders)
def orders() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            rx.hstack(search_order_component(), create_order_modal(), justify="center", gap="3"),
            view_order_modal(),
            edit_order_modal(),
            rx.table.root(
                rx.table.header(get_table_header()),
                rx.table.body(rx.foreach(OrderView.data, get_table_body)),
                width="80vw",
                background_color="#FFF8E1",
                border_radius="20px",
            ),
            pagination_controls(),
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
