# della_soft/views/CustomerView.py
# ============================================================================
#  CustomerView – DIV opcional (puede quedar vacío)
# ============================================================================

import reflex as rx
from typing import Optional, TYPE_CHECKING

# ─── Modelos / Servicios ────────────────────────────────────────────────
from ..models.CustomerModel import Customer
from ..services.CustomerService import (
    select_all_customer_service,
    select_by_parameter_service,
    create_customer_service,
    delete_customer_service,
    update_customer_service,
)

if TYPE_CHECKING:  # para evitar import circular en tiempo de chequeo
    from .MenuView import MenuView  # noqa: F401


# ╔═══════════════════════════════════════════════════════════════════════╗
#║                                STATE                                  ║
#╚═══════════════════════════════════════════════════════════════════════╝
class CustomerView(rx.State):
    # Campos del formulario
    id: int = 0
    ci: str = ""
    div: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    contact: str = ""

    # Tabla / búsqueda
    customers: list[Customer] = []
    customer_search: str = ""
    error_message: str = ""

    # Paginación
    offset: int = 0
    limit: int = 5
    total_items: int = 0

    # ──────────────────────────── CARGA INICIAL ─────────────────────────
    @rx.event
    async def load_customers(self):
        self.customers = await select_all_customer_service()
        self.total_items = len(self.customers)
        self.customers = self.customers[self.offset : self.offset + self.limit]
        self.set()

    # ─────────────────────────── Paginación ────────────────────────────
    @rx.event
    async def next_page(self):
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            await self.load_customers()

    @rx.event
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

    # ───────────────────────────── Búsqueda ─────────────────────────────
    @rx.event
    async def search_on_change(self, value: str):
        self.customer_search = value
        await self.get_customer_by_parameter()

    async def get_customer_by_parameter(self):
        self.customers = await select_by_parameter_service(self.customer_search)
        self.total_items = len(self.customers)
        self.offset = 0
        self.customers = self.customers[: self.limit]
        self.set()

    # ──────────────────────────── CRUD: CREATE ──────────────────────────
    @rx.event
    async def create_customer(self, data: dict):
        try:
            div_val = int(data["div"]) if str(data["div"]).strip() else ""
            create_customer_service(
                ci=data["ci"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                contact=data["contact"],
                div=div_val,
            )
            await self.load_customers()
            yield rx.toast("Cliente creado ✅")
            self.error_message = ""
        except Exception as e:
            self.error_message = f"Error: {e}"
            yield rx.toast(self.error_message, color_scheme="red")

    # ──────────────────────────── CRUD: UPDATE ──────────────────────────
    @rx.event
    async def update_customer(self, form_data: dict):
        try:

            div_val = int(form_data["div"]) if str(form_data["div"]).strip() else ""
            update_customer_service(
                id=int(form_data["id"]),
                ci=int(form_data["ci"]),
                first_name=form_data["first_name"],
                last_name=form_data["last_name"],
                contact=form_data["contact"],
                div=div_val,
            )
            await self.load_customers()
            yield rx.toast("Cliente actualizado 💾")
            self.error_message = ""
        except Exception as e:
            self.error_message = f"Error al actualizar: {e}"
            yield rx.toast(self.error_message, color_scheme="red")

    # ──────────────────────────── CRUD: DELETE ──────────────────────────
    @rx.event
    async def delete_user_by_id(self, cid: int):
        delete_customer_service(cid)
        await self.load_customers()

    # ─────────────── Cargar datos en el modal de edición ────────────────
    @rx.event
    def values(
        self,
        cid: int,
        ci: str,
        div: Optional[int],
        first_name: str,
        last_name: str,
        contact: str,
    ):
        self.id = cid
        self.ci = ci
        self.div = div
        self.first_name = first_name
        self.last_name = last_name
        self.contact = contact

    # ───────────────────── Setters rápidos (inputs) ─────────────────────
    @rx.event
    def set_id(self, v: str):        self.id = int(v or 0)

    @rx.event
    def set_ci(self, v: str):        self.ci = v

    @rx.event
    def set_div(self, v: str):       self.div = int(v) if v.strip() else None

    @rx.event
    def set_first_name(self, v: str): self.first_name = v

    @rx.event
    def set_last_name(self, v: str):  self.last_name = v

    @rx.event
    def set_contact(self, v: str):    self.contact = v


# ═══════════════════════ COMPONENTES UI ═════════════════════════════════
def get_title():
    return rx.text(
        "Clientes",
        size="7",
        weight="bold",
        color="#3E2723",
        fontFamily="DejaVu Sans Mono",
    )


@rx.page(on_load=CustomerView.load_customers)
def customers() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            main_actions_bar(),
            rx.table.root(
                rx.table.header(get_table_header()),
                rx.table.body(rx.foreach(CustomerView.customers, get_table_body)),
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


# ─── Tabla ──────────────────────────────────────────────────────────────
def get_table_header():
    return rx.table.row(
        rx.table.column_header_cell("Cédula"),
        rx.table.column_header_cell("Nombre"),
        rx.table.column_header_cell("Apellido"),
        rx.table.column_header_cell("Contacto"),
        rx.table.column_header_cell("Div"),
        rx.table.column_header_cell("Acciones"),
        color="#3E2723",
        background_color="#A67B5B",
    )


def get_table_body(customer: Customer):
    return rx.table.row(
        rx.table.cell(customer.ci),
        rx.table.cell(customer.first_name),
        rx.table.cell(customer.last_name),
        rx.table.cell(customer.contact),
        rx.table.cell(
            rx.cond(
                customer.div,
                customer.div,
                ""
            )
        ),
        rx.table.cell(
            rx.hstack(
                update_customer_dialog(customer),
                delete_user_dialog(customer.id),
            )
        ),
        color="#3E2723",
    )


# ─── Search + Alta ──────────────────────────────────────────────────────
def search_customer_input():
    return rx.input(
        placeholder="Buscar cliente",
        background_color="#3E2723",
        placeholder_color="white",
        color="white",
        on_change=CustomerView.search_on_change,
    )


def create_customer_form():
    return rx.form(
        rx.vstack(
            rx.grid(
                rx.text("Cédula:", color="white"),
                rx.input(name="ci", placeholder="Cédula", background_color="#5D4037", color="white"),
                rx.text("Nombre:", color="white"),
                rx.input(name="first_name", placeholder="Nombre", background_color="#5D4037", color="white"),
                rx.text("Apellido:", color="white"),
                rx.input(name="last_name", placeholder="Apellido", background_color="#5D4037", color="white"),
                rx.text("Contacto:", color="white"),
                rx.input(name="contact", placeholder="Contacto", background_color="#5D4037", color="white"),
                rx.text("Div:", color="white"),
                rx.input(name="div", placeholder="Div", background_color="#5D4037", color="white"),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            rx.dialog.close(
                rx.button(rx.icon("save", size=22), type="submit",
                          background_color="#3E2723", size="2", variant="solid")
            ),
            spacing="3",
        ),
        on_submit=CustomerView.create_customer,
        style={"width": "100%", "gap": "3", "padding": "3"},
        align="center",
        justify="center",
        debug=True,
    )


def update_customer_form():
    return rx.form(
        rx.vstack(
            rx.input(name="id", type="hidden", value=CustomerView.id),
            rx.grid(
                rx.text("Cédula:", color="white"),
                rx.input(name="ci", value=CustomerView.ci,
                         on_change=CustomerView.set_ci, background_color="#5D4037", color="white"),
                rx.text("Nombre:", color="white"),
                rx.input(name="first_name", value=CustomerView.first_name,
                         on_change=CustomerView.set_first_name, background_color="#5D4037", color="white"),
                rx.text("Apellido:", color="white"),
                rx.input(name="last_name", value=CustomerView.last_name,
                         on_change=CustomerView.set_last_name, background_color="#5D4037", color="white"),
                rx.text("Contacto:", color="white"),
                rx.input(name="contact", value=CustomerView.contact,
                         on_change=CustomerView.set_contact, background_color="#5D4037", color="white"),
                rx.text("Div:", color="white"),
                rx.input(
                    name="div",
                    value=rx.cond(CustomerView.div, CustomerView.div, ""),
                    on_change=CustomerView.set_div,
                    background_color="#5D4037",
                    color="white",
                ),
                columns="1fr 2fr",
                gap="3",
                width="100%",
            ),
            rx.divider(color="white"),
            rx.text(CustomerView.error_message, color="white"),
            rx.dialog.close(
                rx.button(rx.icon("save", size=22), type="submit",
                          background_color="#3E2723", size="2", variant="solid")
            ),
            spacing="3",
        ),
        on_submit=CustomerView.update_customer,
        style={"width": "100%", "gap": "3", "padding": "3"},
        align="center",
        justify="center",
        debug=True,
    )


# ─── Dialogs ────────────────────────────────────────────────────────────
def create_customer_dialog():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(rx.icon("plus", size=22), background_color="#3E2723",
                      size="2", variant="solid")
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title("Crear Cliente"),
                create_customer_form(),
                justify="center",
                align="center",
                direction="column",
            ),
            background_color="#A67B5B",
        ),
    )


def update_customer_dialog(customer):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("square-pen", size=22),
                background_color="#3E2723",
                size="2",
                variant="solid",
                on_click=lambda _=None, c=customer: CustomerView.values(
                    c.id, c.ci, c.div, c.first_name, c.last_name, c.contact
                ),
            )
        ),
        rx.dialog.content(
            rx.flex(
                rx.dialog.title("Actualizar Cliente"),
                update_customer_form(),
                justify="center",
                align="center",
                direction="column",
            ),
            background_color="#A67B5B",
        ),
    )


def delete_user_dialog(cid: int):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(rx.icon("trash", size=22), background_color="#3E2723",
                      size="2", variant="solid")
        ),
        rx.dialog.content(
            rx.dialog.title("Eliminar Cliente"),
            rx.dialog.description("¿Seguro que desea eliminar este cliente?"),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancelar", color_scheme="gray", variant="soft")
                ),
                rx.dialog.close(
                    rx.button("Confirmar",
                              on_click=CustomerView.delete_user_by_id(cid),
                              background_color="#3E2723", size="2", variant="solid")
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            background_color="#A67B5B",
        ),
    )


# ─── Barra de búsqueda + alta ───────────────────────────────────────────
def main_actions_bar():
    return rx.hstack(
        search_customer_input(),
        create_customer_dialog(),
        justify="center",
    )


# ─── Controles de paginación ────────────────────────────────────────────
def pagination_controls():
    return rx.hstack(
        rx.button(rx.icon("arrow-left", size=22), on_click=CustomerView.prev_page,
                  is_disabled=CustomerView.offset <= 0,
                  background_color="#3E2723", size="2", variant="solid"),
        rx.text(CustomerView.current_page, " de ", CustomerView.num_total_pages),
        rx.button(rx.icon("arrow-right", size=22), on_click=CustomerView.next_page,
                  is_disabled=CustomerView.offset + CustomerView.limit >= CustomerView.total_items,
                  background_color="#3E2723", size="2", variant="solid"),
        justify="center",
        color="#3E2723",
    )
