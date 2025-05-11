import reflex as rx
from typing import List


class StockView(rx.State):

    selected_tab: str = "product"
    prod_columns: List[str] = ["Producto", "Cantidad", "Mínimo", "Acciones"]
    ing_columns: List[str] = ["Ingrediente", "Cantidad", "Mínimo", "Medida", "Acciones"]

    product_rows: list[dict] = []
    ingredient_rows: list[dict] = []

    offset: int = 0
    limit: int = 5
    total_items: int = 0
    _page_data: list[dict] = []

    @rx.event
    async def set_tab(self, tab: str):
        self.selected_tab = tab
        self.offset = 0
        await self.load_stock()

    @rx.event
    async def load_stock(self):
        rows = self.product_rows if self.selected_tab == "product" else self.ingredient_rows
        self.total_items = len(rows)
        self._page_data = rows[self.offset : self.offset + self.limit]

    @rx.event
    async def next_page(self):
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            await self.load_stock()

    @rx.event
    async def prev_page(self):
        if self.offset > 0:
            self.offset -= self.limit
            await self.load_stock()

    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items + self.limit - 1) // self.limit, 1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.var
    def page_rows(self) -> list[dict]:
        return self._page_data

def get_title():
    return rx.text(
        "Control de Stock",
        size="7",
        weight="bold",
        color="#3E2723",
        fontFamily="DejaVu Sans Mono",
    )


def tab_button(label: str, value: str):
    return rx.button(
        label,
        size="2",
        variant=rx.cond(StockView.selected_tab == value, "solid", "soft"),
        background_color=rx.cond(StockView.selected_tab == value, "#3E2723", "#A67B5B"),
        color="white",
        border_radius="0",
        padding_x="1.5em",
        on_click=lambda: StockView.set_tab(value),
    )


def tabs_bar():
    return rx.hstack(
        tab_button("Stock de Productos", "product"),
        tab_button("Stock de Ingredientes", "ingredient"),
        width="100%",
        margin_bottom="0.5em",
        justify="start",
    )

def get_table_header():
    return rx.table.row(
        rx.foreach(
            rx.cond(
                StockView.selected_tab == "product",
                StockView.prod_columns,
                StockView.ing_columns,
            ),
            lambda c: rx.table.column_header_cell(c),
        ),
        color="#3E2723",
        background_color="#A67B5B",
    )

def prod_row(row: dict):
    return rx.table.row(
        rx.table.cell(row["name"]),
        rx.table.cell(row["qty"]),
        rx.table.cell(row["min"]),
        rx.table.cell(acciones_cell()),
        color="#3E2723",
    )


def ing_row(row: dict):
    return rx.table.row(
        rx.table.cell(row["name"]),
        rx.table.cell(row["qty"]),
        rx.table.cell(row["min"]),
        rx.table.cell(row["measure"]),
        rx.table.cell(acciones_cell()),
        color="#3E2723",
    )


def acciones_cell():
    return rx.hstack(
        rx.button(
            rx.icon("square-pen", size=22),
            background_color="#3E2723",
            size="2",
            variant="solid",
        ),
        rx.button(
            rx.icon("trash", size=22),
            background_color="#3E2723",
            size="2",
            variant="solid",
        ),
        spacing="2",
    )


def get_table_body(row: dict):
    return rx.cond(
        StockView.selected_tab == "product",
        prod_row(row),
        ing_row(row),
    )

def pagination_controls():
    return rx.hstack(
        rx.button(
            rx.icon("arrow-left", size=22),
            on_click=StockView.prev_page,
            is_disabled=StockView.offset <= 0,
            background_color="#3E2723",
            size="2",
            variant="solid",
        ),
        rx.text(StockView.current_page, " de ", StockView.num_total_pages),
        rx.button(
            rx.icon("arrow-right", size=22),
            on_click=StockView.next_page,
            is_disabled=StockView.offset + StockView.limit >= StockView.total_items,
            background_color="#3E2723",
            size="2",
            variant="solid",
        ),
        justify="center",
        color="#3E2723",
    )

def stock():
    return rx.box(
        rx.vstack(
            get_title(),
            tabs_bar(),
            rx.table.root(
                rx.table.header(get_table_header()),
                rx.table.body(rx.foreach(StockView.page_rows, get_table_body)),
                width="80vw",
                background_color="#FFF8E1",
                border_radius="20px",
            ),
            pagination_controls(),
            spacing="5",
            align="center",
            width="80vw",
        ),
        display="flex",
        justifyContent="center",
        alignItems="flex-start",
        text_align="center",
        background_color="#FDEFEA",
        width="92vw",
        height="80vh",
    )
