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

    def login(self):
        engine= connect()
        with Session(engine) as session:
            query = select(Customer).where(Customer.username == self.username)
            user = session.exec(query).first()

            if user and user.password and verify_password(self.password, user.password):
                self.is_logged_in = True
                self.current_user_id = user.id
                self.error = ""
                return rx.redirect("/menu")
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
        return rx.redirect("/menu")

    def register(self):
        engine= connect()
        with Session(engine) as session:
            existing = session.exec(select(Customer).where(Customer.username == self.username)).first()
            if existing:
                self.error = "Nombre de usuario ya existe"
                return

            new_user = Customer(
                first_name=self.first_name,
                last_name=self.last_name,
                contact=self.contact,
                username=self.username,
                password=hash_password(self.password)
            )
            session.add(new_user)
            session.commit()
            self.error = ""
            return rx.redirect("/menu")
