import reflex as rx

from rxconfig import config

from della_soft.models import RolModel

from typing import Any, List, Dict

from ..models.CustomerModel import Customer

from ..services.CustomerService import select_all_customer_service, select_by_parameter_service, create_customer_service, delete_customer_service, select_by_id_service, get_total_items_service

import asyncio

class CustomerView(rx.State):
    customers:list[Customer]
    customer_search: str
    error_message: str = '' 
    offset: int = 0
    limit: int = 5  # Número de clientes por página
    total_items: int = 0  # Total de clientes
    

    async def load_customers(self):
        """Carga clientes con paginación."""
        all_customers = select_all_customer_service()
        self.total_items = len(all_customers)  # Cuenta el total de clientes
        self.customers = all_customers[self.offset : self.offset + self.limit]  # Aplica paginación

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

    #num_total_pages = (total_items + limit - 1) // limit  # Corrige el cálculo

    async def get_customer_by_parameter(self):
        self.customers = select_by_parameter_service(self)


    def get_customer_by_parameter(self):
        self.customers = select_by_parameter_service(self.customer_search)
    
    def search_on_change(self, value: str):
        self.customer_search = value


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
        
    

@rx.page(on_load=CustomerView.load_customers)
def customers() -> rx.Component:
    return rx.flex(
        rx.heading('Clientes', align='center'),
        rx.hstack(
            search_user_component(), 
            create_user_dialog_component(),
            justify='center',
            style={"margin-top": "auto"}
        ),
        table_customer(CustomerView.customers),
        pagination_controls(),
        direction='column',
        style = {"width": "60vw", "margin": "auto"}

        
         

    )

def table_customer(list_customer: list[Customer]) -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell('Cedula'),
                rx.table.column_header_cell('Nombre'),
                rx.table.column_header_cell('Apellido'),	
                rx.table.column_header_cell('Contacto'),	
                rx.table.column_header_cell('Div'),
                rx.table.column_header_cell('Accion') 
            )
        ),
        rx.table.body(
            rx.foreach(list_customer, row_table)
        )
    )

def row_table (customer: Customer) -> rx.Component:  
    return rx.table.row(
        rx.table.cell(customer.id),
        rx.table.cell(customer.first_name),
        rx.table.cell(customer.last_name),
        rx.table.cell(customer.contact),
        rx.table.cell(customer.div),
        rx.table.cell(rx.hstack(
            #rx.button('Editar'),
            delete_user_dialog_component(customer.id)
            ))
                    
            )

def search_user_component () ->rx.Component:
    return rx.hstack(
        rx.input(placeholder='Buscar cliente', on_change=CustomerView.search_on_change),
        rx.button('Buscar', on_click=CustomerView.get_customer_by_parameter)
    )

def create_customer_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(placeholder='Cedula', id='id'),
            rx.input(placeholder='Nombre', name='first_name'),
            rx.input(placeholder='Apellido', name='last_name'),
            rx.input(placeholder='Contacto', name='contact'),
            rx.input(placeholder='Div', name='div'),
            rx.dialog.close(rx.button('Guardar', type='submit')),
            
    ),
    on_submit=CustomerView.create_customer,
     
    )

def create_user_dialog_component() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button('Crear Cliente')),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Crear Cliente'),
                create_customer_form(),  # Formulario de creación de cliente
                justify='center',
                align='center',
                direction='column',
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button('Cancelar', color_scheme='gray', variant='soft')
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            style={"width": "300px"}
        ),
        
    )

def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button(
            "Anterior",
            on_click=CustomerView.prev_page,
            is_disabled=CustomerView.offset <= 0
        ),
        rx.text(  
            CustomerView.current_page, " de ", CustomerView.num_total_pages
        ),
        rx.button(
            "Siguiente",
            on_click=CustomerView.next_page,
            is_disabled=CustomerView.offset + CustomerView.limit >= CustomerView.total_items
        ),
        justify="center"
    )

def delete_user_dialog_component(id: int) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon('trash-2'))),
        rx.dialog.content(
            rx.dialog.title('Eliminar Cliente'),
            rx.dialog.description('¿Está seguro que desea eliminar este cliente?'),
            rx.flex(
                rx.dialog.close(
                    rx.button('Cancelar', color_scheme='gray', variant='soft')
                ),
                rx.dialog.close(
                    rx.button('Confirmar', on_click=CustomerView.delete_user_by_id(id))
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            #style={"width": "300px"}
        ),
        
    )

