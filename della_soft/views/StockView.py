import reflex as rx

class StockView(rx.State):
    pass

def stock() -> rx.Component:
    return rx.text("STOCK")