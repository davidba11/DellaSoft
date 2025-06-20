# OrderDetailView.py
import reflex as rx
from typing import List

from ..services.ProductService import (
    select_all_product_service,
    create_product,
    get_product,
    delete_product_service,
)
from ..models.ProductModel import Product

DESCRIPTION_TEXT="Descripción"

class OrderDetailView(rx.State):
    data: List[Product]
    plain_data: List[Product] = []
    columns: List[str] = ["Nombre", DESCRIPTION_TEXT, "Tipo", "Precio", "Acciones"]
    input_search: str

    offset: int = 0
    limit: int = 3
    total_items: int = 0

    # Contadores por producto
    product_counts: dict[int, int] = {}

    # Valor por defecto para el select de tipo
    value: str = "Precio Por Kilo"

    @rx.event
    async def load_OrderDetails(self):
        # Al abrir el modal: recargar todos los productos y reiniciar contadores a cero
        products = await select_all_product_service()
        self.plain_data = products[:]  # copia completa
        # Inicializar cada contador en 0
        for p in products:
            self.product_counts.setdefault(p.id, 0)
            self.total_items = len(self.plain_data)
            # Cargar página actual
            self.data = self.plain_data[self.offset : self.offset + self.limit]
            self.set()

    @rx.event
    async def reset_product_counts(self):
        products = await select_all_product_service()
        self.plain_data = products[:]
        self.product_counts = {p.id: 0 for p in products}
        self.total_items = len(products)
        self.offset = 0
        self.limit = 3
        self.data = self.plain_data[self.offset : self.offset + self.limit]
        self.set()

    @rx.event
    async def preserve_product_counts(self):
        products = await select_all_product_service()

        if not self.product_counts:
            # Si está vacío, inicializamos en 0
            self.product_counts = {p.id: 0 for p in products}
        else:
            for p in products:
                self.product_counts.setdefault(p.id, 0)

        self.plain_data = products
        self.total_items = len(products)
        self.data = self.plain_data[self.offset : self.offset + self.limit]
        self.set()

    async def next_page(self):
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            await self.preserve_product_counts()


    async def prev_page(self):
        if self.offset > 0:
            self.offset -= self.limit
            await self.preserve_product_counts()


    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items + self.limit - 1) // self.limit, 1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.event
    def increment(self, product_id: int):
        self.product_counts[product_id] = self.product_counts.get(product_id, 0) + 1

    @rx.event
    def decrement(self, product_id: int):
        if self.product_counts.get(product_id, 0) > 0:
            self.product_counts[product_id] -= 1

    @rx.event
    def change_value(self, value: str):
        self.value = value

    @rx.event
    async def insert_OrderDetail_controller(self, form_data: dict):
        try:
            create_product(
                id="",
                name=form_data["name"],
                description=form_data["description"],
                product_type=form_data["product_type"],
                price=form_data["price"],
            )
            yield OrderDetailView.load_OrderDetails()
            self.set()
        except Exception as e:
            print("Error en insert_OrderDetail_controller:", e)

    async def load_OrderDetail_information(self, value: str):
        self.input_search = value.strip()
        await self.get_product()

    async def get_product(self):
        self.data = await get_product(self.input_search)
        # Asegurar contador para cada producto cargado
        for p in self.data:
            self.product_counts.setdefault(p.id, 0)
        self.total_items = len(self.data)
        self.offset = 0
        self.data = self.data[self.offset : self.offset + self.limit]
        self.set()

    @rx.event
    async def delete_OrderDetail_by_id(self, id: int):
        delete_product_service(id)
        await self.load_OrderDetails()

    @rx.var
    def total(self) -> float:
        # Suma precio * cantidad para cada producto
        return sum(
            p.price * self.product_counts.get(p.id, 0)
            for p in self.plain_data
        )

def product_count_cell(product_id: int) -> rx.Component:
    return rx.text(
        OrderDetailView.product_counts[product_id],
        size="4",
        width="40px",
        text_align="center",
    )

def search_order_detail_component() -> rx.Component:
    return rx.hstack(
        rx.input(
            placeholder="Buscar Producto",
            background_color="#3E2723",
            placeholder_color="white",
            color="white",
            on_change=OrderDetailView.load_OrderDetail_information,
            width="80%",
        ),
        justify="center",
        spacing="2",
    )

def create_product_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.hstack(
                rx.input(
                    placeholder="Nombre",
                    name="name",
                    width="40%",
                    background_color="#3E2723",
                    color="white",
                ),
                rx.select(
                    ["Precio Por Kilo", "Precio Fijo"],
                    value=OrderDetailView.value,
                    on_change=OrderDetailView.change_value,
                    name="product_type",
                    background_color="#3E2723",
                    color="white",
                    width="40%",
                ),
                spacing="2",
                justify="center",
            ),
            rx.hstack(
                rx.input(
                    placeholder="Precio",
                    name="price",
                    width="40%",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text_area(
                    placeholder=DESCRIPTION_TEXT,
                    name="description",
                    width="40%",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                spacing="2",
                justify="center",
            ),
            rx.dialog.close(
                rx.button("Guardar", background_color="#3E2723", type="submit")
            ),
            spacing="4",
        ),
        on_submit=OrderDetailView.insert_OrderDetail_controller,
        debug=True,
        align="center",
        justify="center",
    )

def main_actions_form() -> rx.Component:
    return rx.hstack(
        search_order_detail_component(),
        justify="center",
        style={"margin-top": "auto", "width": "100%"},
        gap="4",
    )

def get_table_header() -> rx.Component:
    return rx.table.row(
        rx.table.column_header_cell("Nombre"),
        rx.table.column_header_cell(DESCRIPTION_TEXT),
        rx.table.column_header_cell("Tipo"),
        rx.table.column_header_cell("Precio"),
        rx.table.column_header_cell("Acciones"),
        color="#3E2723",
        background_color="#A67B5B",
    )

def get_table_body(product: Product) -> rx.Component:
    pid = product.id
    return rx.table.row(
        rx.table.cell(rx.text(product.name, text_align="center")),
        rx.table.cell(rx.text(product.description, text_align="center")),
        rx.table.cell(rx.text(product.product_type, text_align="center")),
        rx.table.cell(rx.text(product.price, text_align="center")),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("minus", size=18),
                    type="button",
                    background_color="#3E2723",
                    on_click=lambda pid=pid: OrderDetailView.decrement(pid),
                ),
                product_count_cell(pid),
                rx.button(
                    rx.icon("plus", size=18),
                    type="button",
                    background_color="#3E2723",
                    on_click=lambda pid=pid: OrderDetailView.increment(pid),
                ),
                spacing="2",
                justify="center",
            ),
        ),
    )

def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("arrow-left", size=22),
            on_click=OrderDetailView.prev_page,
            is_disabled=OrderDetailView.offset <= 0,
            background_color="#3E2723",
            size="2",
            variant="solid",
            type="button",
        ),
        rx.text(OrderDetailView.current_page, " de ", OrderDetailView.num_total_pages),
        rx.button(
            rx.icon("arrow-right", size=22),
            on_click=OrderDetailView.next_page,
            is_disabled=OrderDetailView.offset + OrderDetailView.limit
            >= OrderDetailView.total_items,
            background_color="#3E2723",
            size="2",
            variant="solid",
            type="button",
        ),
        justify="center",
    )

@rx.page(on_load=OrderDetailView.load_OrderDetails)
def order_details() -> rx.Component:
    return rx.box(
        rx.vstack(
            main_actions_form(),
            rx.table.root(
                rx.table.header(get_table_header()),
                rx.table.body(rx.foreach(OrderDetailView.data, get_table_body)),
                width="90%",
                border_radius="20px",
            ),
            pagination_controls(),
            spacing="5",
            align="center",
            justify="center",
            style={"margin": "auto"},
        ),
        display="flex",
        flex_direction="column",
        align_items="center",
        justify_content="center",
        width="100%",
        padding="2rem",
    )
