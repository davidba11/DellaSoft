import asyncio
import reflex as rx

from rxconfig import config

from della_soft.models import RolModel

from typing import Any, List, Dict

from ..services.ProductService import select_all_product_service

from ..models.ProductModel import Product

class ProductView(rx.State):
    data: list[Product]
    columns: List[str] = ["Nombre", "Descripción", "Tipo", "Acciones"]

    async def get_all_products(self):
        self.data = select_all_product_service()
        print (self.data)

    def load_products(self):
        asyncio.create_task(self.get_all_products())

    def insert_product(product):
        pass


def show_data(product: Product):
    return rx.table.row(
        rx.table.cell(product.name),
        rx.table.cell(product.description),
        rx.table.cell(product.product_type),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("square-pen", size=22),
                    rx.text("Edit", size="3"),
                    background_color="#3E2723",
                    size="2",
                    variant="solid",
                    #on_click=lambda: Product.edit_product(products),
                ),
            ),
        ),
        color="#3E2723",
    )

@rx.page(on_load=ProductView.load_products)
def products() -> rx.Component:

    return rx.box(
        rx.vstack(
            rx.text(
                "Productos",
                size="9",
                weight="bold",
                color="#3E2723",
                high_contrast=True,
                fontFamily="DejaVu Sans Mono",
                width="80%",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell(ProductView.columns[0]),
                        rx.table.column_header_cell(ProductView.columns[1]),
                        rx.table.column_header_cell(ProductView.columns[2]),
                        rx.table.column_header_cell(ProductView.columns[3]),
                        color="#3E2723",
                        background_color="#A67B5B",
                    ),
                ),
                rx.table.body(
                    rx.foreach(ProductView.data, show_data)
                ),
                width="80%",
                background_color="#FFF8E1",
                border_radius="20px",
            ),
            display="flex",
            justifyContent="center",
            alignItems="center",
            padding="30px",
            width="100%",
        ),
        flex_grow="1",
        text_align="center",
        background_color="#FAE3D9",
        height="100vh",
    )