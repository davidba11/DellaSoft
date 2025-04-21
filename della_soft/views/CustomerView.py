import reflex as rx

from rxconfig import config

from della_soft.models import RolModel

from typing import Any, List, Dict

from ..models.CustomerModel import Customer

from ..services.CustomerService import select_all_customer_service, select_by_parameter_service, create_customer_service, delete_customer_service, select_by_id_service, get_total_items_service, update_customer_service

import asyncio

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .MenuView import MenuView

class CustomerView(rx.State):
    customers: list[Customer]
    customer_search: str
    error_message: str = '' 
    offset: int = 0
    limit: int = 5  # Número de clientes por página
    total_items: int = 0  # Total de clientes
    id: int = 0
    first_name: str = ""
    last_name: str = ""
    contact: str = ""
    div: int = 0
    ci: str = ''
    error_message: str = ""

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
        print(data)
        try:
            new_customer = create_customer_service(ci=data['ci'], first_name=data['first_name'], last_name=data['last_name'], contact=data['contact'], div=data['div'])
            await self.load_customers()
            #self.customers = self.customers + [new_customer]
            yield rx.toast('Cliente creado.')
            self.error_message = ""
        except BaseException as e:
            print(e)
            self.error_message = "Error: El cliente ya existe."
            
    async def delete_user_by_id(self, id):
        self.customers = delete_customer_service(id)
        await self.load_customers()

    def values(self, customer: Customer):
        self.id = customer.id
        self.first_name = customer.first_name
        self.last_name = customer.last_name
        self.contact = customer.contact
        self.div   = customer.div
        self.ci   = customer.ci
    
    @rx.event
    async def update_customer(self, form_data: dict):
        print(f'Update customer {form_data}')
        try:
            update_customer_service(
                id=int(form_data["id"]),
                ci=int(form_data["ci"]),
                first_name=form_data["first_name"],
                last_name=form_data["last_name"],
                contact=form_data["contact"],
                div=int(form_data["div"])
            )
            await self.load_customers()
            yield rx.toast('Cliente actualizado.')
            self.error_message = ""
        except Exception as e:
            print(e)
            self.error_message = f"Error al actualizar: {e}"

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
        rx.table.column_header_cell('Acciones'), 
        color="#3E2723",
        background_color="#A67B5B",
    )

def get_table_body(customer: Customer):
    return rx.table.row(
        rx.table.cell(customer.ci),
        rx.table.cell(customer.first_name),
        rx.table.cell(customer.last_name),
        rx.table.cell(customer.contact),
        rx.table.cell(customer.div),
        rx.table.cell(
            rx.hstack(
                #rx.button(
                    #rx.icon("notebook-pen", size=22),
                    #background_color="#3E2723",
                    #size="2",
                    #variant="solid",
                    #on_click=CustomerView.createOrder(customer.id)
                #),
                update_customer_dialog_component(customer),
                delete_user_dialog_component(customer.id),
            ),
        ),
        color="#3E2723"
    ),
        

def search_customer_component () ->rx.Component:
    return rx.hstack(
        rx.input(placeholder='Buscar cliente', background_color="#3E2723",  placeholder_color="white", color="white", on_change=CustomerView.search_on_change)
    )

def create_customer_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.grid(
                rx.text("Cédula:", color="white"),
                rx.input(
                    placeholder="Cédula",
                    name="ci",
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Nombre:", color="white"),
                rx.input(
                    placeholder="Nombre",
                    name="first_name",
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Apellido:", color="white"),
                rx.input(
                    placeholder="Apellido",
                    name="last_name",
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Contacto:", color="white"),
                rx.input(
                    placeholder="Contacto",
                    name="contact",
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Div:", color="white"),
                rx.input(
                    placeholder="Div",
                    name="div",
                    background_color="#5D4037",
                    placeholder_color="white",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            # Botón de guardar
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
        on_submit=CustomerView.create_customer,
        style={"width": "100%", "gap": "3", "padding": "3"},
        debug=True,
        align="center",
        justify="center",
    )

def update_customer_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name='id', 
                type="hidden", 
                value=CustomerView.id,
                on_change = lambda value: CustomerView.set_id(value)
            ),
            rx.input(
                placeholder='Cédula',
                name='ci',
                # is_disabled=True,
                value=CustomerView.ci,
                on_change = CustomerView.set_ci,
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
            rx.input(
                placeholder='Nombre',
                name='first_name',
                value=CustomerView.first_name,
                on_change=CustomerView.set_first_name,
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
            rx.input(
                placeholder='Apellido',
                name='last_name',
                value=CustomerView.last_name,
                on_change=CustomerView.set_last_name,
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
            rx.input(
                placeholder='Contacto',
                name='contact',
                value=CustomerView.contact,
                on_change=CustomerView.set_contact,
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
            rx.input(
                placeholder='Div',
                name='div',
                value=CustomerView.div,
                on_change=lambda value: CustomerView.set_div(value),
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
            rx.dialog.close(
                rx.button(rx.icon("save", size=22), background_color="#3E2723", type='submit')
            ),
            rx.text(CustomerView.error_message),
            align='center',
            justify='center',
            spacing="2"
        ),
        align='center',
        justify='center',
        border_radius="20px",
        padding="20px",
        on_submit=CustomerView.update_customer
    )


def create_customer_dialog_component() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("plus", size=22),
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
                weight="bold"
            ),
            rx.flex(
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            background_color="#A67B5B",
        ),
        style={"width": "300px"}
    )


def update_customer_dialog_component(customer) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("square-pen", size=22),
                background_color="#3E2723",
                size="2",
                variant="solid",
                on_click=lambda: CustomerView.values(customer)
                )),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Actualizar Cliente'),
                update_customer_form(),  # Formulario de creación de cliente
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
        search_customer_component(), 
        create_customer_dialog_component(),
        justify='center',
        style={"margin-top": "auto"}
    ),

def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("arrow-left", size=22),
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
            rx.icon("arrow-right", size=22),
            on_click=CustomerView.next_page,
            is_disabled=CustomerView.offset + CustomerView.limit >= CustomerView.total_items,
            background_color="#3E2723",
            size="2",
            variant="solid"
        ),
        justify="center",
        color="#3E2723",
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

