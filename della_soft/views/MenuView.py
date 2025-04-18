import reflex as rx

from rxconfig import config

from .ProductView import ProductView, products
from .OrderView import OrderView, orders
from .CustomerView import CustomerView, customers 
#from .RegisterView import register_page
from .UserView import UserView, users
from .Login import login_page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .CustomerView import CustomerView

from ..repositories.LoginRepository import AuthState

class MenuView(rx.State):
    screen: str = "login"

    customer_id: int = ""

    @rx.event
    def display_screen(self, screen: str):
        if screen == "products_view":
            yield ProductView.load_products()
        if screen == "orders_view":
            yield OrderView.load_orders()
        if screen == "customers_view":
            yield CustomerView.load_customers() 
        if screen == "users_view":
            yield UserView.load_customers()  
        if screen == "order_detail":
            yield ProductView.load_products()
        if screen == "logout":
            yield AuthState.logout()
        self.screen = screen
        self.set()

    def display_screen_by_customer(self, screen: str, id: int):
        print(screen)
        yield ProductView.load_products()
        self.screen = screen

def get_title():
    return rx.box(
        rx.heading(
            "Della Soft",
            size="9",
            weight="bold",
            color="#3E2723",
            high_contrast=True,
            fontFamily="DejaVu Sans Mono",
            width="100%",
            text_align="center"
        ),
        padding="1em",
        background_color="#FDEFEA",
        z_index="10"
    )

def get_menu():
    return rx.vstack(
        rx.spacer(),
        rx.cond(
            AuthState.is_logged_in,
            rx.vstack(
                rx.icon("notebook-pen", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("orders_view")),
                rx.icon("user", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("customers_view")),
                # rx.icon("user", color="#3E2727", size=40, on_click=lambda: MenuView.display_screen("users_view")),
                rx.icon("cake", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("products_view")),
                rx.icon("settings", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("users_view")),
            ),
            rx.icon("log-in", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("login"))
        ),
        rx.spacer(),
        rx.cond(
            AuthState.is_logged_in,
            rx.icon("log-out", color="#3E2723", size=40, on_click=lambda:[ MenuView.display_screen("login"), AuthState.logout()])
        ),
        height="100vh",
        align="center",
        justify="center",
        padding_y="2em",
        padding_x="0.5em"
    )

def menu() -> rx.Component:
    return rx.hstack(
        get_menu(),
        rx.box(
            rx.vstack(
                get_title(),
                rx.cond(
                    MenuView.screen == "login",
                    login_page(),
                        rx.cond(
                            AuthState.is_logged_in,
                            rx.box(
                                rx.cond(
                                    MenuView.screen == "products_view",
                                    products(),
                                    rx.cond(
                                        MenuView.screen == "orders_view",
                                        orders(),
                                        rx.cond(
                                            MenuView.screen == "customers_view",
                                            customers(),
                                                rx.cond(
                                                MenuView.screen == "users_view",
                                                users(),
                                                products()
                                                )
                                        )
                                    )
                                ),
                                width="100%",
                                height="calc(100vh - 5em)",
                                padding="2em",
                                overflow="auto"
                            ),
                            rx.text("Por favor inicie sesión para continuar.")
                        )
                    )
                
            ),
            width="100%",
            height="100vh",
            overflow="hidden"
        ),
        height="100vh",
        width="100vw",
        background_color="#FDEFEA"
    )

# Página inicial
index = rx.page(route="/", on_load=MenuView.display_screen("orders_view"))(menu)