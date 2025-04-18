import reflex as rx
from ..repositories.LoginRepository import AuthState

def register_page():
    return rx.center(
        rx.vstack(
            rx.heading("Registro de Usuario", size="6"),
            rx.input(
                placeholder="Nombre",
                on_change=AuthState.set_first_name,
                value=AuthState.first_name
            ),
            rx.input(
                placeholder="Apellido",
                on_change=AuthState.set_last_name,
                value=AuthState.last_name
            ),
            rx.input(
                placeholder="Contacto",
                on_change=AuthState.set_contact,
                value=AuthState.contact
            ),
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
            rx.button("Registrarse", on_click=AuthState.register),
            rx.link("Iniciar sesión", href="/menu"),
            rx.cond(AuthState.error != "", rx.text(AuthState.error, color="red")),
            spacing="4",
            width="100%",
            max_width="400px",
        ),
        height="100vh"
    )

register = rx.page(route="/register")(register_page)