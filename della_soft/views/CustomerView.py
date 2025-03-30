import reflex as rx

from rxconfig import config

from della_soft.models import RolModel

from typing import Any, List, Dict

from ..models.CustomerModel import Customer

from ..services.CustomerService import select_all_customer_service, select_by_parameter_service, create_customer_service, delete_customer_service, select_by_id_service, get_total_items_service

import asyncio

class CustomerView(rx.State):
    customers: list[Customer]
    customer_search: str
    error_message: str = '' 
    offset: int = 0
    limit: int = 5  # Número de clientes por página
    total_items: int = 0  # Total de clientes
    

    async def load_customers(self):
        """Carga clientes con paginación."""
        self.customers = await select_all_customer_service()
        self.total_items = len(self.customers)  # Cuenta el total de clientes
        self.customers = self.customers[self.offset : self.offset + self.limit]  # Aplica paginación
        self.set()

    async def next_page(self):
        """Pasa a la siguiente página si hay más clientes."""
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            await self.load_customers()

    async def prev_page(self):
        """Vuelve a la página anterior."""
        if self.offset > 0:
            self.offset -= self.limit
            await self.load_customers()

    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items + self.limit - 1) // self.limit, 1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1
    
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    async def get_customer_by_parameter(self):
        self.customers = select_by_parameter_service(self)


    async def get_customer_by_parameter(self):
        """Busca clientes por nombre y aplica paginación correctamente."""
        self.customers = await select_by_parameter_service(self.customer_search)  # 🔍 Filtra clientes
        self.total_items = len(self.customers)  # ✅ Guarda total de clientes filtrados
        self.offset = 0  # ✅ Reinicia a la primera página
        self.customers = self.customers[self.offset : self.offset + self.limit]  # ✅ Aplica paginación
        self.set()
    
    async def search_on_change(self, value: str):
        self.customer_search = value
        await self.get_customer_by_parameter()



    async def create_customer(self, data: dict):
        try:
            new_customer = create_customer_service(id=data['id'], first_name=data['first_name'], last_name=data['last_name'], contact=data['contact'], div=data['div'])
            await self.load_customers()
            #self.customers = self.customers + [new_customer]
            yield
            self.error_message = ""
        except BaseException as e:
            # Si ocurre un error, guarda el mensaje de error y muestra el pop-up
            self.error_message = "Error: El cliente ya existe."
            
    async def delete_user_by_id(self, id):
        self.customers = delete_customer_service(id)
        await self.load_customers()

def get_title():
    return rx.text(
        "Clientes",
        size="7",
        weight="bold",
        color="#3E2723",
        high_contrast=True,
        fontFamily="DejaVu Sans Mono",
        width="80%",
    ),
    

@rx.page(on_load=CustomerView.load_customers)
def customers() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            main_actions_form(),
            rx.table.root(
                rx.table.header(
                    get_table_header(),
                ),
                rx.table.body(
                    (rx.foreach(CustomerView.customers, get_table_body))
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

def get_table_header():
    return rx.table.row(
        rx.table.column_header_cell('Cedula'),
        rx.table.column_header_cell('Nombre'),
        rx.table.column_header_cell('Apellido'),	
        rx.table.column_header_cell('Contacto'),	
        rx.table.column_header_cell('Div'),
        rx.table.column_header_cell('Accion'), 
        background_color="#A67B5B",
    )

def get_table_body(customer: Customer):
    return rx.table.row(
        rx.table.cell(customer.id),
        rx.table.cell(customer.first_name),
        rx.table.cell(customer.last_name),
        rx.table.cell(customer.contact),
        rx.table.cell(customer.div),
        rx.table.cell(
            rx.hstack(
                    delete_user_dialog_component(customer.id),
                ),
            ),
            color="#3E2723",
        ),
        

def search_customer_component () ->rx.Component:
    return rx.hstack(
        rx.input(placeholder='Buscar cliente', background_color="#3E2723",  placeholder_color="white", color="white", on_change=CustomerView.search_on_change),
        rx.button( rx.icon("search", size=22),
            rx.text("Buscar", size="3"),
            background_color="#3E2723",
            size="2",
            variant="solid", on_click=CustomerView.get_customer_by_parameter)
    )

def create_customer_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(placeholder='Cedula', id='id', background_color="#3E2723",  placeholder_color="white", color="white"),
            rx.input(placeholder='Nombre', name='first_name', background_color="#3E2723",  placeholder_color="white", color="white"),
            rx.input(placeholder='Apellido', name='last_name', background_color="#3E2723",  placeholder_color="white", color="white"),
            rx.input(placeholder='Contacto', name='contact', background_color="#3E2723",  placeholder_color="white", color="white"),
            rx.input(placeholder='Div', name='div', background_color="#3E2723",  placeholder_color="white", color="white"),
            rx.dialog.close(rx.button('Guardar', background_color="#3E2723", type='submit')),
            align='center',
            justify='center', 
            spacing="2",
            
    ),
    align='center',
    justify='center',
    #direction='column',
    border_radius="20px",
    padding="20px",
    on_submit=CustomerView.create_customer,
     
    )

def create_customer_dialog_component() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("user", size=22),
                rx.text("Crear", size="3"),
                background_color="#3E2723",
                size="2",
                variant="solid",)),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Crear Cliente'),
                create_customer_form(),  # Formulario de creación de cliente
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
        search_customer_component(), 
        create_customer_dialog_component(),
        justify='center',
        style={"margin-top": "auto"}
    ),

def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button(
            "Anterior",
            on_click=CustomerView.prev_page,
            is_disabled=CustomerView.offset <= 0,
            background_color="#3E2723",
            size="2",
            variant="solid"

        ),
        rx.text(  
            CustomerView.current_page, " de ", CustomerView.num_total_pages
        ),
        rx.button(
            "Siguiente",
            on_click=CustomerView.next_page,
            is_disabled=CustomerView.offset + CustomerView.limit >= CustomerView.total_items,
            background_color="#3E2723",
            size="2",
            variant="solid"
        ),
        justify="center"
    )

def delete_user_dialog_component(id: int) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("trash", size=22),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",)),
        rx.dialog.content(
            rx.dialog.title('Eliminar Cliente'),
            rx.dialog.description('¿Está seguro que desea eliminar este cliente?'),
            rx.flex(
                rx.dialog.close(
                    rx.button('Cancelar', color_scheme='gray', variant='soft')
                ),
                rx.dialog.close(
                    rx.button('Confirmar', on_click=CustomerView.delete_user_by_id(id), background_color="#3E2723",
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

