import reflex as rx

from della_soft.services.CustomerService import create_user_service
from ..models.CustomerModel import Customer
from sqlmodel import select, Session
from ..services.SystemService import verify_password, hash_password
from .ConnectDB import connect
from ..services.RolService import select_all_roles_service
from ..views import MenuView


class AuthState(rx.State):
    username: str = ""
    password: str = ""
    first_name: str = ""
    last_name: str = ""
    contact: str = ""
    id_rol: int | None = None
    current_user_id: int | None = None
    current_id_rol: int | None = None

    error: str = ""
    is_logged_in: bool = False

    roles: list[str] = []
    roles_map: dict = {}
    roles_loaded: bool = False


    def login(self):
        engine = connect()
        with Session(engine) as session:
            query = select(Customer).where(Customer.username == self.username)
            user = session.exec(query).first()

            if user and user.password and verify_password(self.password, user.password):
                self.is_logged_in = True
                self.current_user_id = user.id
                self.error = ""
                self.current_id_rol = user.id_rol
                yield MenuView.MenuView.display_screen("orders_view") 
            else:
                self.error = "Usuario o contraseña incorrectos"
                self.is_logged_in = False
                self.current_user_id = None
    @rx.var 
    def is_admin(self) -> bool:
        return self.current_id_rol == 1

    def logout(self):
        self.is_logged_in = False
        self.current_user_id = None
        self.username = ""
        self.password = ""
        self.error = ""
        from ..views import MenuView


    def set_username(self, value: str):
        self.username = value

    def set_password(self, value: str):
        self.password = value

    def set_first_name(self, value: str):
        self.first_name = value

    def set_last_name(self, value: str):
        self.last_name = value

    def set_contact(self, value: str):
        self.contact = value

    def get_roles(self) -> list[str]:
        roles_result = select_all_roles_service()
        return [rol.description for rol in roles_result]

    def get_roles_map(self) -> dict:
        roles_result = select_all_roles_service()
        return {rol.description: rol.id_rol for rol in roles_result}

    @rx.event
    def load_roles_once(self):
        print(">> Ejecutando load_roles_once...")
        roles_result = select_all_roles_service()
        self.roles = [rol.description for rol in roles_result]
        self.roles_map = {rol.description: rol.id_rol for rol in roles_result}
        self.roles_loaded = True
        print("Lista para el select:", self.roles),
        print("Roles cargados correctamente.")


    def set_selected_role(self, selected_role: str):
        self.id_rol = self.roles_map.get(selected_role)
        print(f"Rol seleccionado: {selected_role} -> ID: {self.id_rol}")

    def register(self):
        if not all([self.username, self.password, self.first_name, self.last_name, self.username, self.password, self.contact, self.id_rol]):
            self.error = "Todos los campos son obligatorios."
            return

        try:
            import random
            new_id = random.randint(1000, 9999)

            create_user_service(
                id=new_id,
                first_name=self.first_name,
                last_name=self.last_name,
                username=self.username,
                password= hash_password(self.password),
                contact=self.contact,
                id_rol=self.id_rol  
            )

            self.error = ""
            yield rx.toast('Usuario registrado!')
            print("Usuario registrado correctamente.")
            
            # yield MenuView.MenuView.display_screen("login") 

        except Exception as e:
            self.error = f"Error al registrar: {e}"