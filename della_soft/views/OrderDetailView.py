import asyncio
import reflex as rx

from rxconfig import config

from typing import Any, List

from ..services.ProductService import select_all_product_service, create_product, get_product, delete_product_service

from ..models.ProductModel import Product

class OrderDetailView(rx.State):
    data: list[dict]
    columns: List[str] = ["Nombre", "Descripción", "Tipo", "Precio", "Acciones"]
    new_product: dict = {}

    input_search: str
    value: str = "Precio Por Kilo"

    offset: int = 0
    limit: int = 5  # Número de productos por página
    total_items: int = 0  # Total de productos

    count: list[int] = 0

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1

    @rx.event
    def change_value(self, value: str):
        self.value = value

    
    '''async def get_all_products(self):
        data = await select_all_product_service()
        #print("Datos desde la BD:", data)
        return data'''

    #@rx.event
    async def load_products(self):
        self.data = await select_all_product_service()
        self.total_items = len(self.data)
        self.data = self.data [self.offset : self.offset + self.limit]
        #print("Productos obtenidos:", self.data)
        #yield
        #self.set()

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
    
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.event
    async def insert_product_controller(self, form_data: dict):
        try:
            new_product = create_product(id="", name=form_data['name'], description=form_data['description'], product_type=form_data['product_type'], price=form_data['price'])
            yield OrderDetailView.load_products()
            self.set()
        except BaseException as e:
            print(e.args)

    def load_product_information(self, value: str):
        self.input_search = value

    def get_product(self):
        self.data = get_product(self.input_search)

    @rx.event
    async def delete_product_by_id(self, id):
        self.data = delete_product_service(id)
        await self.load_products()

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
            on_change=OrderDetailView.load_product_information,
        ),
        rx.button(
            rx.icon("search", size=22),
            rx.text("Buscar", size="3"),
            background_color="#3E2723",
            size="2",
            variant="solid",
            on_click=lambda: OrderDetailView.get_product,
        ),
    )

def create_product_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.hstack(
                rx.input(placeholder='Nombre', name='name', width="100%", background_color="#3E2723", color="white"),
                rx.select(
                    ["Precio Por Kilo", "Precio Fijo"],
                    value=OrderDetailView.value,
                    on_change=OrderDetailView.change_value,
                    name='product_type', background_color="#3E2723",  placeholder_color="white", color="white"
                ),
                align='center',
                justify='center', 
                spacing="2",
            ),
            rx.hstack(
                rx.input(placeholder='Precio', 
                name='price', width="100%",background_color="#3E2723",  placeholder_color="white", color="white"),
                rx.text_area(placeholder='Descripción', description='description', name='description', background_color="#3E2723",  placeholder_color="white", color="white"),
                align='center',
                justify='center', 
                spacing="2",
            ),
            
            rx.dialog.close(
                rx.button(
                    'Guardar',
                    background_color="#3E2723",
                    type='submit',
                ),
            ),   
        ),
         align='center',
        justify='center',
        border_radius="20px",
        padding="20px",
        on_submit=lambda form_data: OrderDetailView.insert_product_controller(form_data),
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
        rx.table.column_header_cell(OrderDetailView.columns[0]),
        rx.table.column_header_cell(OrderDetailView.columns[1]),
        rx.table.column_header_cell(OrderDetailView.columns[2]),
        rx.table.column_header_cell(OrderDetailView.columns[3]),
        rx.table.column_header_cell(OrderDetailView.columns[4]),
        color="#3E2723",
        background_color="#A67B5B",
    ),

def action():
    return rx.hstack(
        rx.button(
            "Decrement",
            color_scheme="ruby",
            on_click=State.decrement,
        ),
        rx.heading(State.count, font_size="2em"),
        rx.button(
            "Increment",
            color_scheme="grass",
            on_click=State.increment,
        ),
        spacing="4",
    )

def get_table_body(product: Product):
    return rx.table.row(
        rx.table.cell(product.name),
        rx.table.cell(product.description),
        rx.table.cell(product.product_type),
        rx.table.cell(product.price),
        rx.table.cell(
            rx.hstack(
               #delete_product_dialog_component(product.id)
            ),
        ),
        color="#3E2723",
    )

@rx.page(on_load=OrderDetailView.load_products)
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
                    rx.foreach(OrderDetailView.data, get_table_body)
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
            "Anterior",
            on_click=OrderDetailView.prev_page,
            is_disabled=OrderDetailView.offset <= 0,
            background_color="#3E2723",
            size="2",
            variant="solid"

        ),
        rx.text(  
            OrderDetailView.current_page, " de ", OrderDetailView.num_total_pages
        ),
        rx.button(
            "Siguiente",
            on_click=OrderDetailView.next_page,
            is_disabled=OrderDetailView.offset + OrderDetailView.limit >= OrderDetailView.total_items,
            background_color="#3E2723",
            size="2",
            variant="solid"
        ),
        justify="center"
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
                    rx.button('Confirmar', on_click=OrderDetailView.delete_product_by_id(id), background_color="#3E2723",
                size="2",
                variant="solid")
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            #style={"width": "300px"}
        ),
        
    )
