import reflex as rx

from rxconfig import config

from della_soft.screens import Menu
from della_soft.screens import CustomerView
from della_soft.screens import Product
from della_soft.screens import Order

#FrontEnd
def index():
    return rx.text("Login")

app = rx.App()
app.add_page(Menu.menu, route="/menu")
app.add_page(index)
app.add_page(CustomerView.Customer, route="/customers")
app.add_page(Product.products, route="/products")
app.add_page(Order.orders, route="/orders")