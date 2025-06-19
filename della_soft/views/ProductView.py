import asyncio
import reflex as rx

from della_soft.repositories.LoginRepository import AuthState
from rxconfig import config

from typing import Any, List

from ..services.ProductService import select_all_product_service, create_product, get_product, delete_product_service, update_product_service

from ..models.ProductModel import Product

DESCRIPTION_TEXT="Descripción"
BASIC_TEXT="Precio Por Kilo"

class ProductView(rx.State):
    data: list[Product]
    columns: List[str] = ["Nombre", DESCRIPTION_TEXT, "Tipo", "Precio", "Acciones"]
    new_product: dict = {}

    input_search: str
    value: str = BASIC_TEXT

    offset: int = 0
    limit: int = 5  # Número de productos por página
    total_items: int = 0  # Total de productos

    id: int = 0
    name: str = ""
    description: str = ""
    product_type: str = ""
    price: int = 0
    error_message: str = ""

    @rx.event
    def change_value(self, value: str):
        self.value = value

    #@rx.event
    async def load_products(self):
        self.data = await select_all_product_service()
        self.total_items = len(self.data)
        self.data = self.data [self.offset : self.offset + self.limit]

    async def next_page(self):
        """Pasa a la siguiente página si hay más productos."""
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            await self.load_products()

    async def prev_page(self):
        """Vuelve a la página anterior."""
        if self.offset > 0:
            self.offset -= self.limit
            await self.load_products()

    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items + self.limit - 1) // self.limit, 1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.event
    async def insert_product_controller(self, form_data: dict):
        try:
            create_product(id="", name=form_data['name'], description=form_data['description'], product_type=form_data['product_type'], price=form_data['price'])
            yield ProductView.load_products()
            self.set()
        except BaseException as e:
            print(e.args)
            raise

    async def load_product_information(self, value: str):
        self.input_search = value
        await self.get_product()

    async def get_product(self):
        self.data = await get_product(self.input_search)
        self.total_items = len(self.data)  # ✅ Guarda total de clientes filtrados
        self.offset = 0  # ✅ Reinicia a la primera página
        self.data = self.data[self.offset : self.offset + self.limit]  # ✅ Aplica paginación
        self.set()

    @rx.event
    async def delete_product_by_id(self, id):
        self.data = delete_product_service(id)
        await self.load_products()

    def values(self, product: Product):
        self.id = product.id
        self.name = product.name
        self.description = product.description
        self.product_type = product.product_type
        self.price = product.price

    @rx.event
    async def update_product(self, form_data: dict):
        print(f'Update product {form_data}')
        try:
            update_product_service(
                id=int(form_data["id"]),
                name=(form_data["name"]),
                description=form_data["description"],
                product_type=form_data["product_type"],
                price=int(form_data["price"]),
            )
            await self.load_products()
            yield rx.toast('Producto actualizado.')
            self.error_message = ""
        except Exception as e:
            print(e)
            self.error_message = f"Error al actualizar: {e}"

def get_title():
    return rx.text(
        "Productos",
        size="7",
        weight="bold",
        color="#3E2723",
        high_contrast=True,
        fontFamily="DejaVu Sans Mono",
        width="80%",
    ),

def search_product_component () ->rx.Component:
    return rx.hstack(
        rx.input(
            placeholder='Buscar Producto',
            background_color="#3E2723", 
            placeholder_color="white", 
            color="white",
            on_change=ProductView.load_product_information,
        ),
    )

def update_product_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name='id', 
                type="hidden", 
                value=ProductView.id,
                on_change = lambda value: ProductView.set_id(value)),
            
            rx.grid(
                rx.text("Nombre:", color="white"),
                rx.input(
                    placeholder="Nombre",
                    name="name",
                    value=ProductView.name,
                    on_change= ProductView.set_name,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                ),
                rx.text("Categoría:", color="white"),
                rx.select(
                    [BASIC_TEXT, "Precio Fijo"],
                    value=ProductView.product_type,
                    on_change=ProductView.set_product_type,	
                    name="product_type",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            # Precio
            rx.grid(
                rx.text("Precio:", color="white"),
                rx.input(
                    placeholder="Precio",
                    name="price",
                    value=ProductView.price,
                    on_change=lambda value: ProductView.set_price(value),
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            # Descripción
            rx.grid(
                rx.text("Descripción:", color="white"),
                rx.text_area(
                    placeholder=DESCRIPTION_TEXT,
                    name="description",
                    value=ProductView.description,
                    on_change = ProductView.set_description,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                    rows="3",
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
        on_submit=ProductView.update_product,
        style={"width": "100%", "gap": "3", "padding": "3"},
        debug=True,
        align="center",
        justify="center",
        )

def create_product_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            # Nombre y Categoría
            rx.grid(
                rx.text("Nombre:", color="white"),
                rx.input(
                    placeholder="Nombre",
                    name="name",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                ),
                rx.text("Categoría:", color="white"),
                rx.select(
                    [BASIC_TEXT, "Precio Fijo"],
                    value=ProductView.value,
                    on_change=ProductView.change_value,
                    name="product_type",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            # Precio
            rx.grid(
                rx.text("Precio:", color="white"),
                rx.input(
                    placeholder="Precio",
                    name="price",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            # Descripción
            rx.grid(
                rx.text("Descripción:", color="white"),
                rx.text_area(
                    placeholder=DESCRIPTION_TEXT,
                    name="description",
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                    width="100%",
                    rows="3",
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
        on_submit=ProductView.insert_product_controller,
        style={"width": "100%", "gap": "3", "padding": "3"},
        debug=True,
        align="center",
        justify="center",
    )


def create_product_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=22),
                background_color="#3E2723",
                size="2",
                variant="solid",
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Crear Producto'),
                create_product_form(),  # Formulario de creación de producto
                justify='center',
                align='center',
                direction='column',
                weight="bold"
            ),
            background_color="#A67B5B",
        ),
        style={"width": "300px"}
    )

def update_product_dialog_component(product) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("square-pen", size=22),
                background_color="#3E2723",
                size="2",
                variant="solid",
                on_click=lambda: ProductView.values(product)
                )),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Actualizar Cliente'),
                update_product_form(),  # Formulario de creación de cliente
                justify='center',
                align='center',
                direction='column',
                weight="bold"
            ),
            background_color="#A67B5B",
        ),
        style={"width": "300px"}
    )

def main_actions_form():
    return rx.hstack(
        search_product_component(), 
        rx.cond(AuthState.is_admin, create_product_modal()),
        justify='center',
        style={"margin-top": "auto"}
    ),

def get_table_header():
    return rx.table.row(
        rx.table.column_header_cell(ProductView.columns[0]),
        rx.table.column_header_cell(ProductView.columns[1]),
        rx.table.column_header_cell(ProductView.columns[2]),
        rx.table.column_header_cell(ProductView.columns[3]),
        rx.table.column_header_cell(ProductView.columns[4]),
        color="#3E2723",
        background_color="#A67B5B",
    ),

def get_table_body(product: Product):
    return rx.table.row(
        rx.table.cell(product.name),
        rx.table.cell(product.description),
        rx.table.cell(product.product_type),
        rx.table.cell(product.price),
        rx.table.cell(
            rx.cond(
                AuthState.is_admin,
                rx.hstack(
                update_product_dialog_component(product),
               delete_product_dialog_component(product.id)
        ),
                None  # Si NO es admin, no muestra nada en Acciones
            ),
        ),
        color="#3E2723",
    )

def products() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            main_actions_form(),
            rx.table.root(
                rx.table.header(
                    get_table_header(),
                ),
                rx.table.body(
                    rx.foreach(ProductView.data, get_table_body)
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
            on_click=ProductView.prev_page,
            is_disabled=ProductView.offset <= 0,
            background_color="#3E2723",
            size="2",
            variant="solid"

        ),
        rx.text(  
            ProductView.current_page, " de ", ProductView.num_total_pages
        ),
        rx.button(
            rx.icon("arrow-right", size=22),
            on_click=ProductView.next_page,
            is_disabled=ProductView.offset + ProductView.limit >= ProductView.total_items,
            background_color="#3E2723",
            size="2",
            variant="solid"
        ),
        justify="center",
        color="#3E2723",
    )
def delete_product_dialog_component(id: int) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("trash", size=22),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",)),
        rx.dialog.content(
            rx.dialog.title('Eliminar Producto'),
            rx.dialog.description('¿Está seguro que desea eliminar este producto?'),
            rx.flex(
                rx.dialog.close(
                    rx.button('Cancelar', color_scheme='gray', variant='soft')
                ),
                rx.dialog.close(
                    rx.button('Confirmar', on_click=ProductView.delete_product_by_id(id), background_color="#3E2723",
                size="2",
                variant="solid")
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
    )
