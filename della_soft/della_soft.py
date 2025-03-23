import reflex as rx

from rxconfig import config

from della_soft.views import Menu
from della_soft.views import CustomerView
from della_soft.views import Product
from della_soft.views import Order

#FrontEnd
def index():
    return rx.text("Login")

#Publicación de páginas
app = rx.App()
app.add_page(Menu.menu, route="/menu")
app.add_page(index)
#app.add_page(CustomerView.customers, route="/customers")
app.add_page(Product.products, route="/products")
app.add_page(Order.orders, route="/orders")