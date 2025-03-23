import reflex as rx

from rxconfig import config

from della_soft.views import Menu
from della_soft.views import CustomerView
from della_soft.views import ProductView
from della_soft.views import OrderView

#FrontEnd
def index():
    return rx.text("Login")

app = rx.App()
app.add_page(Menu.menu, route="/menu")
app.add_page(index)
app.add_page(CustomerView.customers, route="/customers")
app.add_page(ProductView.products, route="/products", title='Productos')
app.add_page(OrderView.orders, route="/orders")