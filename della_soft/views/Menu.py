import reflex as rx

from rxconfig import config

def menu() -> rx.Component:
    return rx.box(
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
    ),