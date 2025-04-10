import reflex as rx
from ..repositories.LoginRepository import AuthState

@rx.page(route="/register", on_load=AuthState.load_roles)
def register_page():
    return rx.flex(
        rx.vstack(
            rx.heading("Registro de Usuario", size="6", color="#3E2723", margin_top="3em"),
            rx.input(placeholder="Nombre", on_change=AuthState.set_first_name, width="100%", background_color="#3E2723", color="white", placeholder_color="white"),
            rx.input(placeholder="Apellido", on_change=AuthState.set_last_name, width="100%", background_color="#3E2723", color="white", placeholder_color="white"),
            rx.input(placeholder="Contacto", on_change=AuthState.set_contact, width="100%", background_color="#3E2723", color="white", placeholder_color="white"),
            rx.input(placeholder="Usuario", on_change=AuthState.set_username, width="100%", background_color="#3E2723", color="white", placeholder_color="white"),
            rx.input(placeholder="Contraseña", type="password", on_change=AuthState.set_password, width="100%", background_color="#3E2723", color="white", placeholder_color="white"),
            rx.select(
                items=AuthState.roles,
                name="id_rol",
                placeholder="Seleccione un rol",
                background_color="#3E2723",
                color="white",
                width="100%"
            ),
            rx.button(rx.hstack(rx.icon("user-plus"), rx.text("Registrarse")), on_click=AuthState.register, width="100%", background_color="#3E2723", color="white"),
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