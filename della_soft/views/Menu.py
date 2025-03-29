import reflex as rx

from rxconfig import config

from .ProductView import ProductView, products

from .OrderView import OrderView, orders

class MenuView(rx.State):
    screen: str = "orders_view"

    @rx.event
    def display_screen(self, screen: str):
        if(screen=="products_view"):
            yield ProductView.load_products()
        if(screen=="orders_view"):
            yield OrderView.load_orders()    
        self.screen=screen
        self.set()

def get_title():
    return rx.text(
        "Della Soft",
        size="9",
        weight="bold",
        color="#3E2723",
        high_contrast=True,
        fontFamily="DejaVu Sans Mono",
        width="100%",
        display="flex",
        justifyContent="center",
        alignItems="center",
    ),

def get_menu():
    return rx.vstack(
        rx.icon("notebook-pen", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("orders_view")),
        rx.icon("user",color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("customers")),
        rx.icon("cake",color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("products_view")),
        rx.icon("settings", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("users")),
        rx.spacer(),
        rx.icon("log-out", color="#3E2723", size=40),
        height="100%",
    ),

def menu() -> rx.Component:
    return rx.vstack(
        get_title(),
        rx.hstack(
            get_menu(),
            rx.container(
                rx.cond(
                    MenuView.screen=="products_view",
                    products(),
                    rx.cond(
                        MenuView.screen=="orders_view",
                        orders()
                    ),
                ),
            ),
        ),
        height="100vh",
        background_color="#FDEFEA",
    ),