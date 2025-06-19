import reflex as rx
from ..repositories.LoginRepository import AuthState

def login_page():
    return rx.flex(
        rx.vstack(
            rx.heading("Iniciar Sesión", size="6", color="#3E2723", margin_top="3em"),
            rx.input(placeholder="Usuario", on_change=AuthState.set_username, width="100%", background_color="#3E2723", color="white", placeholder_color="white"),
            rx.input(placeholder="Contraseña", type="password", password=True, on_change=AuthState.set_password, width="100%", background_color="#3E2723", color="white", placeholder_color="white"),
            rx.button(
                rx.hstack(rx.icon("log-in"), rx.text("Entrar")),
                on_click=AuthState.login,
                width="100%",
                background_color="#3E2723",
                color="white"
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

login = rx.page(route="/login")(login_page) 