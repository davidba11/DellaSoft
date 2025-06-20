import reflex as rx

from rxconfig import config

from .ProductView import ProductView, products
from .OrderView import OrderView, orders
from .CustomerView import CustomerView, customers
from .UserView import UserView, users
from .Login import login_page
from .POSView import POSView, pos_page
from .IngredientView import IngredientView, ingredients
from .RecipeView import RecipeView, recipes
from .StockView import StockView, stock
from .TransactionView import TransactionView, transactions 
from .DashboardView import dashboard_view, DashboardState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .CustomerView import CustomerView

from ..repositories.LoginRepository import AuthState

class MenuView(rx.State):
    screen: str = "login"

    customer_id: int

    @rx.event
    def display_screen(self, screen: str):
        if screen == "products_view":
            yield ProductView.load_products()
        if screen == "orders_view":
            yield OrderView.load_orders()
        if screen == "customers_view":
            yield CustomerView.load_customers() 
        if screen == "users_view":
            yield UserView.load_customers()  
        if screen == "order_detail":
            yield ProductView.load_products()
        if screen == "pos_view":
            yield POSView.load_date()
        if screen == "ingredients_view":
            yield IngredientView.load_ingredients()
        if screen == "stock_view":
            yield StockView.load_stock()
        if screen == "transactions_view":
            yield TransactionView.reset_filters_today()
            yield TransactionView.load_transactions()
        if screen == "reports_view":
            yield DashboardState.load_dashboard_data()
            
        if screen == "logout":
            yield AuthState.logout()
        self.screen = screen
        self.set()

    def display_screen_by_customer(self, screen: str, id: int):
        yield ProductView.load_products()
        self.screen = screen

def get_title():
    return rx.box(
        rx.heading(
            "Della Soft",
            size="9",
            weight="bold",
            color="#3E2723",
            high_contrast=True,
            fontFamily="DejaVu Sans Mono",
            width="100%",
            text_align="left"
        ),
        padding="1em",
        background_color="#FDEFEA",
        z_index="10"
    )

def menu_icon(icon_name: str, label: str, on_click=None) -> rx.Component:
    return rx.tooltip(
        rx.icon(
            icon_name,
            color="#3E2723",
            size=40,
            on_click=on_click,
        ),
        content=label,
        side="right",
        side_offset=8,
    )

def get_menu():
    return rx.vstack(
        rx.spacer(),
        rx.cond(
            AuthState.is_logged_in,
            rx.vstack(
                menu_icon("notebook-pen", "Pedidos", on_click=lambda: MenuView.display_screen("orders_view")),
                menu_icon("user", "Clientes", on_click=lambda: MenuView.display_screen("customers_view")),
                menu_icon("cake", "Productos", on_click=lambda: MenuView.display_screen("products_view")),
                menu_icon("circle-dollar-sign", "Caja", on_click=lambda: MenuView.display_screen("pos_view")),
                rx.cond(
                    AuthState.is_admin,
                    menu_icon("banknote", "Transacciones", on_click=lambda: MenuView.display_screen("transactions_view")),
                    None
                ),
                rx.cond(
                    AuthState.is_admin,
                    menu_icon("bar-chart", "Dashboard",  on_click=lambda: MenuView.display_screen("reports_view")),
                    None
                ),
                menu_icon("cherry", "Ingredientes", on_click=lambda: MenuView.display_screen("ingredients_view")),
                menu_icon("book-open-text", "Recetas", on_click=lambda: MenuView.display_screen("recipes_view")),
                menu_icon("list-checks", "Stock", on_click=lambda: MenuView.display_screen("stock_view")),
                menu_icon("settings", "Usuarios", on_click=lambda: MenuView.display_screen("users_view")),
            ),
            menu_icon("log-in", "Ingresar", on_click=lambda: MenuView.display_screen("login")),
        ),
        rx.spacer(),
        rx.cond(
            AuthState.is_logged_in,
            menu_icon("log-out", "Salir", on_click=lambda: [MenuView.display_screen("login"), AuthState.logout()]),
        ),
        height="100vh",
        align="center",
        justify="center",
        padding_y="2em",
        padding_x="0.5em"
    )

def menu() -> rx.Component:
    return rx.hstack(
        get_menu(),
        rx.box(
            get_title(),
            rx.cond(
                MenuView.screen == "login",
                login_page(),
                rx.cond(
                    AuthState.is_logged_in,
                    rx.box(
                        rx.cond(
                MenuView.screen == "products_view",
                products(),
                rx.cond(
                    MenuView.screen == "customers_view",
                    customers(),
                    rx.cond(
                        MenuView.screen == "users_view",
                        users(),
                        rx.cond(
                            MenuView.screen == "pos_view",
                            pos_page(),
                            rx.cond(
                                MenuView.screen == "transactions_view",
                                transactions(),
                                rx.cond(
                                    MenuView.screen == "ingredients_view",
                                    ingredients(),
                                    rx.cond(
                                        MenuView.screen == "recipes_view",
                                        recipes(),
                                        rx.cond(
                                            MenuView.screen == "stock_view",
                                            stock(),
                                            rx.cond(
                                                MenuView.screen == "reports_view",
                                                dashboard_view(),
                                                orders()  # Default fallback si ninguna coincide
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ),
                        width="100%",
                        height="calc(100vh - 5em)",
                        padding="2em",
                        overflow="auto"
                    ),
                    rx.text("Por favor inicie sesión para continuar.")
                ),
            ),
            width="100%",
            height="100vh",
            overflow="hidden"
        ),
        height="100vh",
        width="100vw",
        background_color="#FDEFEA"
    )

# Página inicial
index = rx.page(route="/", on_load=MenuView.display_screen("orders_view"))(menu)
