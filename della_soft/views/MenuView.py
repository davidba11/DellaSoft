import reflex as rx
from rxconfig import config

from .ProductView import ProductView, products
from .OrderView import OrderView, orders
from .CustomerView import CustomerView, customers

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .CustomerView import CustomerView

class MenuView(rx.State):
    screen: str = "orders_view"
    customer_id: int = ""

    @rx.event
    def display_screen(self, screen: str):
        if screen == "products_view":
            yield ProductView.load_products()
        if screen == "orders_view":
            yield OrderView.load_orders()
        if screen == "customers_view":
            yield CustomerView.load_customers()
        if screen == "order_detail":
            yield ProductView.load_products()
        self.screen = screen
        self.set()

    def display_screen_by_customer(self, screen: str, id: int):
        print(screen)
        yield ProductView.load_products()
        self.screen = screen


def get_title():
    return rx.text(
        "Della Soft",
        size="9",
        weight="bold",
        color="#3E2723",
        high_contrast=True,
        fontFamily="DejaVu Sans Mono",
        width="100%",
        text_align="center",
        margin_bottom="2",
    ),


def get_menu():
    return rx.vstack(
        rx.icon("notebook-pen", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("orders_view")),
        rx.icon("user", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("customers_view")),
        rx.icon("cake", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("products_view")),
        rx.icon("settings", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("users")),
        rx.spacer(),
        rx.icon("log-out", color="#3E2723", size=40),
        spacing="6",
        align="center",
        justify="start",
        style={"padding": "1rem"},
    )


def menu() -> rx.Component:
    return rx.box(
        rx.vstack(
            get_title(),
            rx.hstack(
                rx.box(
                    get_menu(),
                    style={
                        "width": "80px",
                        "minWidth": "80px",
                        "backgroundColor": "#FDEFEA",
                    },
                ),
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
                                orders()
                            )
                        )
                    ),
                    style={
                        "flex": "1",
                        "width": "100%",
                        "padding": "1rem",
                    },
                ),
                spacing="0",
            ),
            style={"width": "100%"},
            spacing="2",
        ),
        display="flex",
        flex_direction="column",
        background_color="#FDEFEA",
        min_height="100vh",
        width="100%",
    )