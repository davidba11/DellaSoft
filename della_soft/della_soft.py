import reflex as rx

from rxconfig import config

from della_soft.views import MenuView
from della_soft.views import CustomerView
from della_soft.views import ProductView
from della_soft.views import OrderView
from della_soft.views import OrderDetailView

#FrontEnd
def index():
    return rx.text("Login")

#Publicación de páginas
app = rx.App()
app.add_page(MenuView.menu, route="/menu")
app.add_page(index)
app.add_page(CustomerView.customers, route="/customers", title='Clientes')  
app.add_page(ProductView.products, route="/products", title='Productos')
app.add_page(OrderView.orders, route="/orders")