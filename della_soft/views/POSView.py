import reflex as rx

from rxconfig import config

class POSView(rx.State):
    pass

def pos() -> rx.Component:
    return rx.text("Módulo de Caja")