import reflex as rx

from rxconfig import config

from .ProductView import ProductView, products

class MenuView(rx.State):
    screen: str = "orders"

    @rx.event
    def display_screen(self, screen: str):
        if(screen=="products_view"):
            yield ProductView.load_products()
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
        rx.icon("notebook-pen", color="#3E2723", size=40, on_click=lambda: MenuView.display_screen("orders")),
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
                    products()
                ),
            ),
        ),
        height="100vh",
        background_color="#FDEFEA",
    ),
    '''return rx.box(
        rx.vstack(
            rx.text(
                "Della Campagna Pastelería",
                size="9",
                weight="bold",
                color="#3E2723",
                high_contrast=True,
                fontFamily="DejaVu Sans Mono",
            ),
            rx.box(
                rx.vstack(
                    rx.text(
                        "Menú Principal",
                        size="6",
                        weight="bold",
                        color="#D81B60",
                        high_contrast=True,
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "Clientes",
                            type="submit",
                            background_color="#D81B60",
                            border_radius="5px",
                            width="45%",
                            height="20%",
                            margin="12px",
                            padding="12px",
                            on_click=rx.redirect("/customers"),
                        ),
                        rx.spacer(),
                        rx.button(
                            "Productos",
                            type="submit",
                            background_color="#D81B60",
                            border_radius="5px",
                            width="45%",
                            height="20%",
                            margin="12px",
                            padding="12px",
                            on_click=rx.redirect("/products"),
                        ),
                        width="100vh",
                    ),
                    rx.hstack(
                        rx.button(
                            "Pedidos",
                            type="submit",
                            background_color="#D81B60",
                            border_radius="5px",
                            width="45%",
                            height="20%",
                            margin="12px",
                            padding="12px",
                            on_click=rx.redirect("/orders"),
                        ),
                        rx.spacer(),
                        rx.button(
                            "-",
                            type="submit",
                            background_color="#D81B60",
                            border_radius="5px",
                            width="45%",
                            height="20%",
                            margin="12px",
                            padding="12px",
                        ),
                        width="100vh",
                    ),
                ),
                flex_grow="1",
                background_color="#FFF8E1",
                margin="12px",
                padding="12px",
            ),
            display="flex",
            justifyContent="center",
            alignItems="center",
            height="100vh",
            padding="30px"
        ),
        flex_grow="1",
        text_align="center",
        background_color="#FAE3D9",
        height="100vh",
    ),'''