import reflex as rx
from ..models.CustomerModel import Customer
from sqlmodel import select, Session
from ..services.SystemService import verify_password, hash_password
from .ConnectDB import connect



class AuthState(rx.State):
    username: str = ""
    password: str = ""
    error: str = ""
    is_logged_in: bool = False
    current_user_id: int | None = None
    first_name: str = ""
    last_name: str = ""
    contact: str = ""
    id_rol: int | None = None
    roles: list[str] = []
    rol_map: dict[str, int] = {}

    def login(self):
        engine = connect()
        with Session(engine) as session:
            query = select(Customer).where(Customer.username == self.username)
            user = session.exec(query).first()

            if user and user.password and verify_password(self.password, user.password):
                self.is_logged_in = True
                self.current_user_id = user.id
                self.error = ""
                from ..views import MenuView
                yield MenuView.MenuView.display_screen("orders_view") 
            else:
                self.error = "Usuario o contraseña incorrectos"
                self.is_logged_in = False
                self.current_user_id = None

    def logout(self):
        self.is_logged_in = False
        self.current_user_id = None
        self.username = ""
        self.password = ""
        self.error = ""
        from ..views import MenuView
        #yield MenuView.MenuView.display_screen("menu")  # ⬅️ Redirige visualmente
        #return rx.redirect("/menu")

    def register(self):
        engine = connect()
        with Session(engine) as session:
        # Validación: usuario ya existe
            existing = session.exec(
            select(Customer).where(Customer.username == self.username)
        ).first()
        if existing:
            self.error = "Nombre de usuario ya existe."
            return

        # Validación: rol seleccionado
        if not self.id_rol:
            self.error = "Debe seleccionar un rol."
            return

        # Validación: campos obligatorios
        if not all([self.first_name, self.last_name, self.contact, self.username, self.password]):
            self.error = "Todos los campos son obligatorios."
            return

        # Crear nuevo usuario
        new_user = Customer(
            first_name=self.first_name,
            last_name=self.last_name,
            contact=self.contact,
            username=self.username,
            password=hash_password(self.password),
            id_rol=self.id_rol
        )

        session.add(new_user)
        session.commit()
        self.error = ""

        # Redirigir al login después de registrar
        return rx.redirect("/login")


    @rx.event
    def load_roles(self):
        engine = connect()
        with Session(engine) as session:
            # Aquí asumimos que Customer.rol está relacionado con RolModel
            Rol = Customer.rol.property.mapper.class_
            result = session.exec(select(Rol)).all()
            self.roles = [rol.nombre for rol in result]
            self.rol_map = {rol.nombre: rol.id_rol for rol in result}
