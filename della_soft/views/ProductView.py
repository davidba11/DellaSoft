import asyncio
import reflex as rx

from rxconfig import config

from typing import Any, List

from ..services.ProductService import select_all_product_service, create_product, get_product

from ..models.ProductModel import Product

class ProductView(rx.State):
    data: list[Product]
    columns: List[str] = ["Nombre", "Descripción", "Tipo", "Acciones"]
    new_product: dict = {}

    input_search: str
    value: str = "Precio Por Kilo"

    @rx.event
    def change_value(self, value: str):
        self.value = value

    async def get_all_products(self):
        self.data = await select_all_product_service()
        print (self.data)
        return self.data

    @rx.event
    async def load_products(self):
        self.data = await self.get_all_products()
        print (self.data)

    async def insert_product_controller(self, form_data: dict):
        try:
            print(form_data)
            new_product = create_product(id="", name=form_data['name'], description=form_data['description'], product_type=form_data['product_type'])
            print(new_product)
            await self.get_all_products()
            #self.data.append(self.new_product)
        except BaseException as e:
            print(e.args)

    def load_product_information(self, value: str):
        self.input_search = value

    def get_product(self):
        self.data = get_product(self.input_search)

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
            on_change=ProductView.load_product_information,
        ),
        rx.button(
            rx.icon("search", size=22),
            rx.text("Buscar", size="3"),
            background_color="#3E2723",
            size="2",
            variant="solid",
            on_click=lambda: ProductView.get_product,
        ),
    )

def create_product_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.hstack(
                rx.input(placeholder='Nombre', name='name', width="100%"),
                rx.select(
                    ["Precio Por Kilo", "Precio Fijo"],
                    value=ProductView.value,
                    on_change=ProductView.change_value,
                    name='product_type'
                ),
            ),
            rx.text_area(placeholder='Descripción', description='description', name='description'),
            rx.dialog.close(
                rx.button(
                    'Guardar',
                    type='submit',
                ),
            ),   
        ),
        on_submit=lambda form_data: ProductView.insert_product_controller(form_data),
        debug=True,
    )

def create_product_modal() -> rx.Component:
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
                rx.dialog.title('Crear Producto'),
                create_product_form(),  # Formulario de creación de producto
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
        search_product_component(), 
        create_product_modal(),
        justify='center',
        style={"margin-top": "auto"}
    ),

def get_table_header():
    return rx.table.row(
        rx.table.column_header_cell(ProductView.columns[0]),
        rx.table.column_header_cell(ProductView.columns[1]),
        rx.table.column_header_cell(ProductView.columns[2]),
        rx.table.column_header_cell(ProductView.columns[3]),
        color="#3E2723",
        background_color="#A67B5B",
    ),

def get_table_body(product: Product):
    return rx.table.row(
        rx.table.cell(product.name),
        rx.table.cell(product.description),
        rx.table.cell(product.product_type),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("square-pen", size=22),
                    rx.text("Edit", size="3"),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                ),
            ),
        ),
        color="#3E2723",
    )

@rx.page(on_load=ProductView.load_products)
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