import reflex as rx

from rxconfig import config

class OrderView(rx.State):
    pass

def orders():
    return rx.text("Listado de Pedidos")