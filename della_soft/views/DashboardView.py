import reflex as rx

from ..services.DashboardService import (
    get_stock_rotation_data_month,
    get_top_products_month,
    get_orders_per_day_month,
)
from .ReportPDF import (
    generate_stock_rotation_pdf,
    generate_top_products_pdf,
    generate_orders_per_day_pdf,
)

MESSAGE_NOT_FOUND="No hay datos para mostrar."
MESSAGE_DOWNLOAD="Descargar PDF"

class DashboardState(rx.State):
    stock_rotation_data: list = []
    top_products_data: list = []
    orders_by_day_data: list = []

    resumen_stock: str = ""
    resumen_top: str = ""
    resumen_orders: str = ""

    @rx.event
    async def load_dashboard_data(self):
        self.stock_rotation_data = await get_stock_rotation_data_month()
        self.top_products_data = await get_top_products_month()
        self.orders_by_day_data = await get_orders_per_day_month()

        if self.stock_rotation_data:
            prod_mas_vendido = max(self.stock_rotation_data, key=lambda x: x["Cantidad Vendida (Rotación)"])
            total_vendidos = sum(x["Cantidad Vendida (Rotación)"] for x in self.stock_rotation_data)
            self.resumen_stock = (
                f'Producto con mayor rotación: {prod_mas_vendido["Producto"]} '
                f'({prod_mas_vendido["Cantidad Vendida (Rotación)"]} vendidos). '
                f'Total de productos vendidos: {total_vendidos}.'
            )
        else:
            self.resumen_stock = MESSAGE_NOT_FOUND

        if self.top_products_data:
            prod_top = self.top_products_data[0]
            self.resumen_top = f'Producto más vendido: {prod_top["Producto"]} ({prod_top["Cantidad Vendida"]} ventas).'
        else:
            self.resumen_top = MESSAGE_NOT_FOUND

        if self.orders_by_day_data:
            total_pedidos = sum(x["Pedidos"] for x in self.orders_by_day_data)
            self.resumen_orders = f'Total de pedidos este mes: {total_pedidos}.'
        else:
            self.resumen_orders = MESSAGE_NOT_FOUND

        self.set()

    @rx.event
    def download_stock_rotation_pdf(self):
        data = list(self.stock_rotation_data)
        url = generate_stock_rotation_pdf(data)
        return rx.download(url)

    @rx.event
    def download_top_products_pdf(self):
        data = list(self.top_products_data)
        url = generate_top_products_pdf(data)
        return rx.download(url)

    @rx.event
    def download_orders_per_day_pdf(self):
        data = list(self.orders_by_day_data)
        url = generate_orders_per_day_pdf(data)
        return rx.download(url)

def dashboard_view() -> rx.Component:
    return rx.box(
        rx.heading("Dashboard Gerencial", size="7", color="#3E2723"),


        rx.card(
            rx.heading("Reporte: Stock vs Rotación", size="5"),
            rx.text(DashboardState.resumen_stock),
            rx.button(
                MESSAGE_DOWNLOAD,
                on_click=DashboardState.download_stock_rotation_pdf,
                color="#fff",
                background_color="#3E2723",
                margin_top="1em"
            ),
            margin_bottom="2em"
        ),

        rx.card(
            rx.heading("Reporte: Top 5 Productos Más Vendidos", size="5"),
            rx.text(DashboardState.resumen_top),
            rx.button(
                MESSAGE_DOWNLOAD,
                on_click=DashboardState.download_top_products_pdf,
                color="#fff",
                background_color="#3E2723",
                margin_top="1em"
            ),
            margin_bottom="2em"
        ),


        rx.card(
            rx.heading("Reporte: Pedidos por Día", size="5"),
            rx.text(DashboardState.resumen_orders),
            rx.button(
                MESSAGE_DOWNLOAD,
                on_click=DashboardState.download_orders_per_day_pdf,
                color="#fff",
                background_color="#3E2723",
                margin_top="1em"
            ),
            margin_bottom="2em"
        ),

        padding="2em",
        margin_top="1em"
    )

