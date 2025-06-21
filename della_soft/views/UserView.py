import reflex as rx

from rxconfig import config
from della_soft.models import RolModel

from typing import Any, List, Dict

from ..models.CustomerModel import Customer
from ..services.CustomerService import (
    delete_customer_service, create_user_service, select_all_users_service,
    select_users_by_parameter_service, update_user_service
)
from ..services.RolService import select_all_roles_service
from ..services.SystemService import hash_password

from ..repositories.LoginRepository import AuthState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .MenuView import MenuView

class UserView(rx.State):
    customers: list[Customer] = []
    customer_search: str = ""
    error_message: str = ''
    offset: int = 0
    limit: int = 5
    total_items: int = 0
    id: int = 0
    first_name: str = ""
    last_name: str = ""
    contact: str = ""
    username: str = ""
    password: str = ""
    id_rol: int = -1
    ci: str = ''
    selected_role: str = ""

    @rx.event
    def set_first_name(self, value: str):
        self.first_name = value
        self.set()

    @rx.event
    def set_last_name(self, value: str):
        self.last_name = value
        self.set()

    @rx.event
    def set_contact(self, value: str):
        self.contact = value
        self.set()

    @rx.event
    def set_username(self, value: str):
        self.username = value
        self.set()

    @rx.event
    def set_password(self, value: str):
        self.password = value
        self.set()

    @rx.event
    def set_ci(self, value: str):
        self.ci = value
        self.set()

    @rx.event
    def set_selected_role(self, value: str):
        self.selected_role = value
        roles_result = select_all_roles_service()
        for rol in roles_result:
            if rol.description == value:
                self.id_rol = rol.id_rol
                break
        else:
            self.id_rol = -1
        self.set()

    @rx.event
    def reset_form(self):
        self.first_name = ""
        self.last_name = ""
        self.contact = ""
        self.username = ""
        self.password = ""
        self.ci = ""
        self.id_rol = -1
        self.selected_role = ""
        self.error_message = ""
        self.set()

    async def load_customers(self):
        self.customers = select_all_users_service()
        self.total_items = len(self.customers)
        self.customers = self.customers[self.offset : self.offset + self.limit]
        self.set()

    async def next_page(self):
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            await self.load_customers()

    async def prev_page(self):
        if self.offset > 0:
            self.offset -= self.limit
            await self.load_customers()

    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items + self.limit - 1) // self.limit, 1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1

    async def get_customer_by_parameter(self):
        self.customers = await select_users_by_parameter_service(self.customer_search)
        self.total_items = len(self.customers)
        self.offset = 0
        self.customers = self.customers[self.offset : self.offset + self.limit]
        self.set()
    
    async def search_on_change(self, value: str):
        self.customer_search = value
        await self.get_customer_by_parameter()

    async def delete_user_by_id(self, id):
        self.customers = delete_customer_service(id)
        await self.load_customers()

    @rx.event
    def register_and_reload(self):
        if self.selected_role == "" or self.id_rol <= 0:
            self.error_message = "Debe seleccionar un rol válido."
            self.set()
            return
        try:
            create_user_service(
                first_name=self.first_name,
                last_name=self.last_name,
                contact=self.contact,
                username=self.username,
                password=hash_password(self.password),
                id_rol=self.id_rol,
                ci=self.ci
            )
            yield type(self).load_customers()
            self.error_message = ""
            self.reset_form()
            self.set()
        except Exception as e:
            self.error_message = f"Error al registrar usuario: {e}"
            self.set()

    @rx.event
    def prepare_edit_user(self, customer_id: int):
        from ..services.CustomerService import select_by_id_service
        customer = select_by_id_service(customer_id)[0]
        yield self.values(customer)

    @rx.event
    def values(self, customer: Customer):
        self.id = customer.id
        self.first_name = customer.first_name
        self.last_name = customer.last_name
        self.contact = customer.contact
        self.username = customer.username
        self.password = customer.password
        self.ci = customer.ci
        self.id_rol = customer.id_rol
        roles_result = select_all_roles_service()
        for rol in roles_result:
            if rol.id_rol == self.id_rol:
                self.selected_role = rol.description
                break
        else:
            self.selected_role = ""
        self.set()

    @rx.event
    async def update_customer(self, form_data: dict):
        try:
            if self.id_rol is None or self.id_rol <= 0:
                self.error_message = "Debe seleccionar un rol válido."
                self.set()
                return

            from ..services.CustomerService import select_by_id_service
            current_user = select_by_id_service(int(form_data["id"]))[0]

            if self.password != current_user.password:
                password_to_save = hash_password(self.password)
            else:
                password_to_save = self.password

            update_user_service(
                id=int(form_data["id"]),
                ci=form_data["ci"],
                first_name=form_data["first_name"],
                last_name=form_data["last_name"],
                contact=form_data["contact"],
                username=form_data["username"],
                password=password_to_save,
                id_rol=self.id_rol
            )

            await self.load_customers()
            yield rx.toast("Usuario actualizado correctamente.")
            self.error_message = ""
            self.set()
        except Exception as e:
            self.error_message = f"Error al actualizar: {e}"
            self.set()

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
            main_actions_form(),   # Botón crear solo admin
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
            spacing="5",
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
        rx.table.cell(customer.username),
        rx.table.cell(
            # Solo muestra los botones si es admin
            rx.cond(
                AuthState.is_admin,
                rx.hstack(
                    update_customer_dialog_component(customer),
                    delete_user_dialog_component(customer.id)
                ),
                None  # Si NO es admin, no muestra nada en Acciones
            ),
        ),
        color="#3E2723"
    ),

def search_customer_component () ->rx.Component:
    return rx.hstack(
        rx.input(
            placeholder='Buscar usuario',
            background_color="#3E2723",
            placeholder_color="white",
            color="white",
            on_change=UserView.search_on_change
        )
    )

def create_user_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.grid(
                rx.text("Cédula:", color="white"),
                rx.input(
                    placeholder="Cédula",
                    name="ci",
                    value=UserView.ci,
                    on_change=UserView.set_ci,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Nombre:", color="white"),
                rx.input(
                    placeholder="Nombre",
                    name="first_name",
                    value=UserView.first_name,
                    on_change=UserView.set_first_name,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Apellido:", color="white"),
                rx.input(
                    placeholder="Apellido",
                    name="last_name",
                    value=UserView.last_name,
                    on_change=UserView.set_last_name,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Contacto:", color="white"),
                rx.input(
                    placeholder="Contacto",
                    name="contact",
                    value=UserView.contact,
                    on_change=UserView.set_contact,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Usuario:", color="white"),
                rx.input(
                    placeholder="Usuario",
                    name="username",
                    value=UserView.username,
                    on_change=UserView.set_username,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Contraseña:", color="white"),
                rx.input(
                    placeholder="Contraseña",
                    name="password",
                    type="password",
                    value=UserView.password,
                    on_change=UserView.set_password,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Rol:", color="white"),
                rx.select(
                    items=[rol.description for rol in select_all_roles_service()],
                    name="role",
                    value=UserView.selected_role,
                    placeholder="Seleccione un rol",
                    on_change=UserView.set_selected_role,
                    background_color="#3E2723",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            rx.dialog.close(
                rx.button(
                    rx.icon("user-plus", size=22),
                    type="submit",
                    background_color="#3E2723",
                    color="white",
                    size="2",
                    variant="solid",
                )
            ),
            rx.cond(UserView.error_message != "", rx.text(UserView.error_message, color="red")),
            spacing="4",
            width="100%",
            max_width="400px",
        ),
        on_submit=UserView.register_and_reload,
        style={"gap": "3", "padding": "3"},
        align="center",
        justify="center",
    ),

def create_customer_dialog_component() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=22),
                background_color="#3E2723",
                size="2",
                variant="solid",
                on_click=UserView.reset_form,
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Crear Usuario'),
                create_user_form(),
                justify='center',
                align='center',
                direction='column',
                weight="bold"
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
                on_change=lambda value: UserView.set_id(value)
            ),
            rx.grid(
                rx.text("Cédula:", color="white"),
                rx.input(
                    placeholder="Cédula",
                    name="ci",
                    value=UserView.ci,
                    on_change=UserView.set_ci,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Nombre:", color="white"),
                rx.input(
                    placeholder="Nombre",
                    name="first_name",
                    value=UserView.first_name,
                    on_change=UserView.set_first_name,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Apellido:", color="white"),
                rx.input(
                    placeholder="Apellido",
                    name="last_name",
                    value=UserView.last_name,
                    on_change=UserView.set_last_name,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Contacto:", color="white"),
                rx.input(
                    placeholder="Contacto",
                    name="contact",
                    value=UserView.contact,
                    on_change=UserView.set_contact,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Usuario:", color="white"),
                rx.input(
                    placeholder="Usuario",
                    name="username",
                    value=UserView.username,
                    on_change=UserView.set_username,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                rx.text("Contraseña:", color="white"),
                rx.input(
                    placeholder="Contraseña",
                    name="password",
                    type="password",
                    value=UserView.password,
                    on_change=UserView.set_password,
                    background_color="#3E2723",
                    placeholder_color="white",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.grid(
                rx.text("Rol:", color="white"),
                rx.select(
                    items=[rol.description for rol in select_all_roles_service()],
                    name="role",
                    value=UserView.selected_role,
                    placeholder="Seleccione un rol",
                    on_change=UserView.set_selected_role,
                    background_color="#3E2723",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
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
            rx.cond(
                UserView.error_message != "",
                rx.text(UserView.error_message, color="red"),
            ),
            spacing="3",
            width="100%",
            max_width="400px",
        ),
        on_submit=UserView.update_customer,
        style={"width": "100%", "gap": "3", "padding": "3"},
        align="center",
        justify="center",
    )

def update_customer_dialog_component(customer) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("square-pen", size=22),
                background_color="#3E2723",
                size="2",
                variant="solid",
                on_click=lambda: UserView.prepare_edit_user(customer.id)
                )),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title('Actualizar Usuario'),
                update_user_form(),
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
        rx.cond(AuthState.is_admin, create_customer_dialog_component()),  # Botón crear solo admin
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
                    rx.button('Confirmar', on_click=UserView.delete_user_by_id(id), background_color="#3E2723",
                size="2",
                variant="solid")
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
        ),
    )
