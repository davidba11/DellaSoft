'''import asyncio
import reflex as rx

from rxconfig import config

from typing import Any, List

from ..services.ProductService import select_all_product_service, create_product, get_product, delete_product_service

from ..models.ProductModel import Product

class OrderDetailView(rx.State):
    data: list[Product]
    columns: List[str] = ["Nombre", "Descripción", "Tipo", "Precio", "Acciones"]
    new_OrderDetail: dict = {}

    input_search: str
    value: str = "Precio Por Kilo"

    offset: int = 0
    limit: int = 5  # Número de OrderDetailos por página
    total_items: int = 0  # Total de OrderDetailos

    @rx.event
    def change_value(self, value: str):
        self.value = value

    
    #async def get_all_OrderDetails(self):
        #data = await select_all_product_service()
        #print("Datos desde la BD:", data)
        #return data

    #@rx.event
    async def load_OrderDetails(self):
        self.data = await select_all_product_service()
        self.total_items = len(self.data)
        self.data = self.data [self.offset : self.offset + self.limit]
        #print("OrderDetailos obtenidos:", self.data)
        #yield
        #self.set()

    async def next_page(self):
        """Pasa a la siguiente página si hay más OrderDetailos."""
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            await self.load_OrderDetails()

    async def prev_page(self):
        """Vuelve a la página anterior."""
        if self.offset > 0:
            self.offset -= self.limit
            await self.load_OrderDetails()

    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items + self.limit - 1) // self.limit, 1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1
    
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.event
    async def insert_OrderDetail_controller(self, form_data: dict):
        try:
            new_OrderDetail = create_product(id="", name=form_data['name'], description=form_data['description'], product_type=form_data['product_type'], price=form_data['price'])
            yield OrderDetailView.load_OrderDetails()
            self.set()
        except BaseException as e:
            print(e.args)

    async def load_OrderDetail_information(self, value: str):
        self.input_search = value
        await self.get_product()

    async def get_product(self):
        self.data = await get_product(self.input_search)
        self.total_items = len(self.data)  # ✅ Guarda total de clientes filtrados
        self.offset = 0  # ✅ Reinicia a la primera página
        self.data = self.data[self.offset : self.offset + self.limit]  # ✅ Aplica paginación
        self.set()

    @rx.event
    async def delete_OrderDetail_by_id(self, id):
        self.data = delete_product_service(id)
        await self.load_OrderDetails()

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

def search_OrderDetail_component () ->rx.Component:
    return rx.hstack(
        rx.input(
            placeholder='Buscar OrderDetailo',
            background_color="#3E2723", 
            placeholder_color="white", 
            color="white",
            on_change=OrderDetailView.load_OrderDetail_information,
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
        on_submit=lambda form_data: OrderDetailView.insert_OrderDetail_controller(form_data),
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
                rx.dialog.title('Crear OrderDetailo'),
                create_product_form(),  # Formulario de creación de OrderDetailo
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
        search_OrderDetail_component(), 
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

def get_table_body(OrderDetail: Product):
    return rx.table.row(
        rx.table.cell(OrderDetail.name),
        rx.table.cell(OrderDetail.description),
        rx.table.cell(OrderDetail.product_type),
        rx.table.cell(OrderDetail.price),
        rx.table.cell(
            rx.hstack(
               delete_OrderDetail_dialog_component(OrderDetail.id)
            ),
        ),
        color="#3E2723",
    )

@rx.page(on_load=OrderDetailView.load_OrderDetails)
def OrderDetails() -> rx.Component:
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
def delete_OrderDetail_dialog_component(id: int) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("trash", size=22),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",)),
        rx.dialog.content(
            rx.dialog.title('Eliminar OrderDetailo'),
            rx.dialog.description('¿Está seguro que desea eliminar este OrderDetailo?'),
            rx.flex(
                rx.dialog.close(
                    rx.button('Cancelar', color_scheme='gray', variant='soft')
                ),
                rx.dialog.close(
                    rx.button('Confirmar', on_click=OrderDetailView.delete_OrderDetail_by_id(id), background_color="#3E2723",
                size="2",
                variant="solid")
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            #style={"width": "300px"}
        ),
        
    )'''

'''import reflex as rx
from typing import List, Dict

class ProductOrderView(rx.State):
    available_products: List[Dict] = [
        {"name": "Producto 1", "price": 10.0},
        {"name": "Producto 2", "price": 20.0},
        {"name": "Producto 3", "price": 30.0},
    ]  # Productos estáticos para la prueba
    selected_products: List[Dict] = []  # Productos seleccionados
    input_search: str = ""  # Campo de búsqueda

    @rx.event
    async def update_search_query(self, value: str):
        """Actualiza el término de búsqueda."""
        self.input_search = value
        self.set()

    @rx.var
    def filter_products(self) -> List[Dict]:
        """Filtra productos según el término de búsqueda."""
        search = self.input_search.lower()
        filtered = [
            product for product in self.available_products
            if search in product["name"].lower()
        ]
        return filtered

    @rx.event
    async def add_product_to_order(self, product: Dict):
        """Añade un producto a la selección si no está duplicado."""
        if product not in self.selected_products:
            self.selected_products.append(product)
            self.set()

    @rx.event
    async def remove_product_from_order(self, product: Dict):
        """Elimina un producto seleccionado."""
        self.selected_products.remove(product)
        self.set()

# Componente de búsqueda y selección de productos
def search_and_select_component() -> rx.Component:
    return rx.vstack(
        # Campo de búsqueda
        rx.input(
            placeholder="Buscar producto...",
            on_change=ProductOrderView.update_search_query,
            background_color="#F0F0F0",
            color="black",
        ),
        # Lista de productos filtrados
        rx.vstack(
            rx.foreach(
                ProductOrderView.filter_products,
                lambda product: rx.hstack(
                    rx.text(product["name"]),
                    rx.button(
                        rx.icon("plus", size=22), 
                        background_color="#3E2723",
                        size="2",
                        variant="solid",
                        on_click=lambda product=product: ProductOrderView.add_product_to_order(product)),
                )
            ),
        ),
        # Mostrar los productos seleccionados
        rx.text("Productos seleccionados:", size="4"),
        rx.vstack(
            rx.foreach(
                ProductOrderView.selected_products,
                lambda product: rx.hstack(
                    rx.text(f"{product['name']} - ${product['price']}"),
                    rx.button(
                        rx.icon("x", size=22), 
                        background_color="#3E2723",
                        size="2",
                        on_click=lambda product=product: ProductOrderView.remove_product_from_order(product)
                    ),
                )
            )
        ),
    )

# Página de orden de productos
def product_order_page() -> rx.Component:
    return rx.box(
        search_and_select_component(),
        padding="20px",
        align="center",
        justify="center",
    )'''