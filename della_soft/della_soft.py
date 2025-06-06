import reflex as rx

from rxconfig import config

from della_soft.views import MenuView
from della_soft.views import CustomerView
from della_soft.views import ProductView
from della_soft.views import OrderView
from della_soft.views import POSView
from della_soft.views import Login
from della_soft.views import RegisterView
from della_soft.repositories.LoginRepository import AuthState

#Publicación de páginas
app = rx.App()
app.add_page(MenuView.menu, route="/menu", on_load=AuthState.load_roles_once)
