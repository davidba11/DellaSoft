import reflex as rx

from rxconfig import config

from della_soft.models import RolModel

from typing import Any, List, Dict

from ..models.CustomerModel import Customer

from ..services.CustomerService import select_all_customer_service, select_by_parameter_service, create_customer_service, delete_customer_service, select_by_id_service, get_total_items_service, create_user_service, select_all_users_service, select_users_by_parameter, select_users_by_parameter_service, update_user_service

import asyncio

from ..repositories.LoginRepository import AuthState

from ..services.SystemService import hash_password

from typing import TYPE_CHECKING

from ..services.RolService import select_all_roles_service


if TYPE_CHECKING:
    from .MenuView import MenuView

class UserView(rx.State):
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
    username: str = ""
    password: str = ""
    id_rol: int = -1
    ci: str = ''
    error_message: str = ""
    selected_role: str = ""

    async def load_customers(self):
        """Carga clientes con paginación."""
        self.customers = await select_all_users_service()
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
        self.customers = select_users_by_parameter_service(self)


    async def get_customer_by_parameter(self):
        """Busca clientes por nombre y aplica paginación correctamente."""
        self.customers = await select_users_by_parameter_service(self.customer_search)  # 🔍 Filtra clientes
        self.total_items = len(self.customers)  # ✅ Guarda total de clientes filtrados
        self.offset = 0  # ✅ Reinicia a la primera página
        self.customers = self.customers[self.offset : self.offset + self.limit]  # ✅ Aplica paginación
        self.set()
    
    async def search_on_change(self, value: str):
        self.customer_search = value
        await self.get_customer_by_parameter()
    
            
    async def delete_user_by_id(self, id):
        self.customers = delete_customer_service(id)
        await self.load_customers()

    @rx.event
    async def register_and_reload(self):
        yield AuthState.register()
        yield await self.load_customers()

    @rx.event
    def prepare_edit_user(self, customer_id: int):
        from ..services.CustomerService import select_by_id_service
        customer = select_by_id_service(customer_id)[0]
        yield self.values(customer)

    @rx.event
    def set_selected_role(self, value: str):
        self.selected_role = value
        from ..services.RolService import select_all_roles_service

        roles_result = select_all_roles_service()
        for rol in roles_result:
            if rol.description == value:
                self.id_rol = rol.id_rol
                break
        else:
            self.id_rol = -1

    @rx.event
    def values(self, customer: Customer):
        from ..services.RolService import select_all_roles_service

        self.id = customer.id
        self.first_name = customer.first_name
        self.last_name = customer.last_name
        self.contact = customer.contact
        self.username = customer.username
        self.password = customer.password
        self.ci = customer.ci
        self.id_rol = customer.id_rol

        roles_result = select_all_roles_service()

        # Buscar la descripción del rol actual
        for rol in roles_result:
            if rol.id_rol == self.id_rol:
                self.selected_role = rol.description
                break
        else:
            self.selected_role = ""

        # 🟢 Reasignar id_rol desde la descripción, sin usar next()
        for rol in roles_result:
            if rol.description == self.selected_role:
                self.id_rol = rol.id_rol
                break

    @rx.event
    async def update_customer(self, form_data: dict):
        print(f'Update customer {form_data}')
        print("🟢 ID de rol antes de guardar:", self.id_rol)

        id_rol_value = self.id_rol
        if isinstance(id_rol_value, int) and id_rol_value > 0:
            update_user_service(
                id=int(form_data["id"]),
                ci=form_data["ci"],
                first_name=form_data["first_name"],
                last_name=form_data["last_name"],
                contact=form_data["contact"],
                username=form_data["username"],
                id_rol=self.id_rol,
                password=hash_password(form_data["password"]),
                
            )
            await self.load_customers()
            yield rx.toast('Usuario actualizado.')
            self.error_message = ""
        else:
            self.error_message = "Debe seleccionar un rol válido."

def get_title():
    return rx.text(
        "Usuarios",
        size="7",
        weight="bold",
        color="#3E2723",
        high_contrast=True,
        fontFamily="DejaVu Sans Mono",
        width="80%",
    ),
    

@rx.page(on_load=UserView.load_customers)
def users() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            main_actions_form(),
            rx.table.root(
                rx.table.header(
                    get_table_header(),
                ),
                rx.table.body(
                    (rx.foreach(UserView.customers, get_table_body))
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
        rx.table.column_header_cell('Usuario'),	
        rx.table.column_header_cell('Accion'), 
        color="#3E2723",
        background_color="#A67B5B",
    )

def get_table_body(customer: Customer):
    return rx.table.row(
        rx.table.cell(customer.ci),
        rx.table.cell(customer.first_name),
        rx.table.cell(customer.last_name),
        rx.table.cell(customer.contact),
        rx.table.cell(customer.username),
        rx.table.cell(
            rx.hstack(
                #rx.button(
                    #rx.icon("notebook-pen", size=22),
                    #background_color="#3E2723",
                    #size="2",
                    #variant="solid",
                    #on_click=CustomerView.createOrder(customer.id)
                #),
                rx.cond(
                    AuthState.is_admin,
                    update_customer_dialog_component(customer),
                    delete_user_dialog_component(customer.id))
                ,
            ),
        ),
        color="#3E2723"
    ),
        


def search_customer_component () ->rx.Component:
    return rx.hstack(
        rx.input(placeholder='Buscar usuario', background_color="#3E2723",  placeholder_color="white", color="white", on_change=UserView.search_on_change)
    )

def create_customer_form() -> rx.Component:
    return rx.flex(
        rx.vstack(

            rx.heading("Registro de Usuario", size="6", color="#3E2723", margin_top="3em"),

            rx.input(
                placeholder="Cedula",
                on_change=AuthState.set_ci,
                width="100%",
                background_color="#3E2723",
                color="white",
                placeholder_color="white"
            ),
            rx.input(
                placeholder="Nombre",
                on_change=AuthState.set_first_name,
                width="100%",
                background_color="#3E2723",
                color="white",
                placeholder_color="white"
            ),

            rx.input(
                placeholder="Apellido",
                on_change=AuthState.set_last_name,
                width="100%",
                background_color="#3E2723",
                color="white",
                placeholder_color="white"
            ),

            rx.input(
                placeholder="Contacto",
                on_change=AuthState.set_contact,
                width="100%",
                background_color="#3E2723",
                color="white",
                placeholder_color="white"
            ),

            rx.input(
                placeholder="Usuario",
                on_change=AuthState.set_username,
                width="100%",
                background_color="#3E2723",
                color="white",
                placeholder_color="white"
            ),

            rx.input(
                placeholder="Contraseña",
                type="password",
                on_change=AuthState.set_password,
                width="100%",
                background_color="#3E2723",
                color="white",
                placeholder_color="white"
            ),

            rx.select(
                items=AuthState.roles,
                placeholder="Seleccione un rol",
                on_change=AuthState.set_selected_role,
                background_color="#3E2723",
                color="white",
                width="100%"
            ),

            rx.dialog.close(rx.button(
                rx.hstack(rx.icon("user-plus"), rx.text("Crear")),
                on_click=UserView.register_and_reload,
                width="100%",
                background_color="#3E2723",
                color="white",
                
            )
            ),

            rx.cond(AuthState.error != "", rx.text(AuthState.error, color="red")),

            spacing="4",
            width="100%",
            max_width="400px"
        ),
        justify="center",
        align="center",
        height="60vh",
        width="100%"
    )

def create_customer_dialog_component() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("plus", size=22),
                rx.text("Crear", size="3"),
                background_color="#3E2723",
                size="2",
                variant="solid",)),
        rx.dialog.content(
            rx.flex(
                #rx.dialog.title('Crear Usuario'),
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

def update_user_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name='id', 
                type="hidden", 
                value=UserView.id,
                on_change = lambda value: UserView.set_id(value)
            ),
            rx.input(
                placeholder='Cédula',
                name='ci',
                # is_disabled=True,
                value=UserView.ci,
                on_change = UserView.set_ci,
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
            rx.input(
                placeholder='Nombre',
                name='first_name',
                value=UserView.first_name,
                on_change=UserView.set_first_name,
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
            rx.input(
                placeholder='Apellido',
                name='last_name',
                value=UserView.last_name,
                on_change=UserView.set_last_name,
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
            rx.input(
                placeholder='Contacto',
                name='contact',
                value=UserView.contact,
                on_change=UserView.set_contact,
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
            rx.input(
                placeholder='Usuario',
                name='username',
                value=UserView.username,
                on_change=UserView.set_username,
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
            rx.input(
                placeholder='Contraseña',
                name='password',
                type='password',
                value=UserView.password,
                on_change=UserView.set_password,
                background_color="#3E2723",
                placeholder_color="white",
                color="white"
            ),
           rx.select(
                items=AuthState.roles,  # lista de descripciones
                #name="id_rol",
                placeholder="Seleccione un rol",
                value=UserView.selected_role,  # string
                on_change=UserView.set_selected_role,
                background_color="#3E2723",
                color="white",
                width="100%"
            ),
            rx.dialog.close(
                rx.button('Actualizar', background_color="#3E2723", type='submit')
            ),
            rx.text(UserView.error_message),
            align='center',
            justify='center',
            spacing="2"
        ),
        align='center',
        justify='center',
        border_radius="20px",
        padding="20px",
        on_submit=UserView.update_customer
    )

def update_customer_dialog_component(customer) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("plus", size=22),
                rx.text("Crear", size="3"),
                background_color="#3E2723",
                size="2",
                variant="solid",
                on_click=lambda: UserView.prepare_edit_user(customer.id)
                
                )),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Actualizar Cliente'),
                update_user_form(),  # Formulario de creación de cliente
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
        rx.cond(AuthState.is_admin, create_customer_dialog_component()),
        justify='center',
        style={"margin-top": "auto"}
    ),

def pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("arrow-left", size=22),
            on_click=UserView.prev_page,
            is_disabled=UserView.offset <= 0,
            background_color="#3E2723",
            size="2",
            variant="solid"
        ),
        rx.text(  
            UserView.current_page, " de ", UserView.num_total_pages
        ),
        rx.button(
            rx.icon("arrow-right", size=22),
            on_click=UserView.next_page,
            is_disabled=UserView.offset + UserView.limit >= UserView.total_items,
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
            rx.dialog.title('Eliminar Usuario'),
            rx.dialog.description('¿Está seguro que desea eliminar este usuario?'),
            rx.flex(
                rx.dialog.close(
                    rx.button('Cancelar', color_scheme='gray', variant='soft')
                ),
                rx.dialog.close(
                    rx.button('Confirmar', on_click=UserView.delete_user_by_id(id), background_color="#3E2723",
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

