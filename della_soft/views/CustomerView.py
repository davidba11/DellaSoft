import reflex as rx

from rxconfig import config

from della_soft.models import RolModel

from typing import Any, List, Dict

class CustomerView(rx.State):
    '''data: list[CustomerBD]
    columns: List[str] = ["Nombre", "Apellido", "Contacto", "Acciones"]

    def edit_customer(customers: list):
        pass

    @rx.event
    def get_customers():
        with rx.session() as session:
            data = session.exec(
                CustomerBD.select()
            ).all()'''


def show_data(customers: list):
    return rx.table.row(
        rx.table.cell(customers[0]),
        rx.table.cell(customers[1]),
        rx.table.cell(customers[2]),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("square-pen", size=22),
                    rx.text("Edit", size="3"),
                    color_scheme="blue",
                    size="2",
                    variant="solid",
                    #on_click=lambda: CustomerBD.edit_customer(customers),
                ),
            ),
        ),
    )
    
def customers():

    return rx.table.root(
        rx.table.header(
            rx.table.row(
                '''rx.table.column_header_cell(CustomerBD.columns[0]),
                rx.table.column_header_cell(CustomerBD.columns[1]),
                rx.table.column_header_cell(CustomerBD.columns[2]),
                rx.table.column_header_cell(CustomerBD.columns[3]),'''
            ),
        ),
        rx.table.body(
            '''rx.foreach(
                CustomerBD.data, show_data
            )'''
        ),
    )