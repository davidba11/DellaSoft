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

#FrontEnd
def index():
    return rx.text("Login")

#Publicación de páginas
app = rx.App()
app.add_page(MenuView.menu, route="/menu", on_load=AuthState.load_roles_once)
app.add_page(index)
app.add_page(CustomerView.customers, route="/customers", title='Clientes')  
app.add_page(ProductView.products, route="/products", title='Productos')
app.add_page(OrderView.orders, route="/orders")
app.add_page(Login.login_page, route="/login")
app.add_page(RegisterView.register_page, route="/register")
app.add_page(POSView.pos_page, route="/pos")
