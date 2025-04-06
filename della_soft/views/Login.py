import reflex as rx
from ..repositories.LoginRepository import AuthState

def login_page():
    return rx.center(
        rx.vstack(
            rx.heading("Iniciar Sesión", size="6"),
            rx.input(
                placeholder="Usuario",
                on_change=AuthState.set_username,
                value=AuthState.username
            ),
            rx.input(
                placeholder="Contraseña",
                type_="password",
                on_change=AuthState.set_password,
                value=AuthState.password
            ),
            rx.button("Entrar", on_click=AuthState.login),
            rx.link("Registrarse", href="/register"),
            rx.cond(AuthState.error != "", rx.text(AuthState.error, color="red")),
            spacing="4",
            width="100%",
            max_width="400px",
        ),
        height="100vh"
    )

login = rx.page(route="/login")(login_page) 