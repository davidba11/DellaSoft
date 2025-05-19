# della_soft/views/TransactionView.py
import reflex as rx
from datetime import date
from typing import List, Dict

from ..services.TransactionService import get_transactions_by_date_range_service
from ..services.CustomerService import select_by_id_service   # para username

# ── columnas (sin “Acciones”) ────────────────────────────────────────────────
TABLE_COLUMNS: List[str] = ["Usuario", "Observación", "Monto", "Fecha", "Estado"]


class TransactionView(rx.State):
    """Estado de la pestaña Transacciones con filtros y paginación."""

    # datos
    transactions: List[Dict] = []          # ↳ solo la página visible
    _all_rows: List[Dict] = []             # ↳ todas las filas filtradas
    total_amount: int = 0                  # suma global de Montos

    # filtros
    start_date: str = date.today().isoformat()
    end_date: str = date.today().isoformat()
    status_filter: str = "TODOS"

    # paginación
    offset: int = 0
    limit: int = 5
    total_items: int = 0

    # ── setters de filtros ──────────────────────────────────────────────────
    @rx.event
    def set_start_date(self, value: str):
        self.start_date = value
        self.set()

    @rx.event
    def set_end_date(self, value: str):
        self.end_date = value
        self.set()

    @rx.event
    def set_status(self, value: str):
        self.status_filter = value
        self.set()

    # ── paginación ──────────────────────────────────────────────────────────
    @rx.event
    def next_page(self):
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
            yield self._refresh_page()

    @rx.event
    def prev_page(self):
        if self.offset > 0:
            self.offset -= self.limit
            yield self._refresh_page()

    @rx.event
    def _refresh_page(self):
        """Mueve solo la ventana visible; no vuelve a consultar la BD."""
        self.transactions = self._all_rows[self.offset : self.offset + self.limit]
        self.set()

    @rx.var
    def num_total_pages(self) -> int:
        return max((self.total_items + self.limit - 1) // self.limit, 1)

    @rx.var
    def current_page(self) -> int:
        return (self.offset // self.limit) + 1

    # ── carga de datos principal (incluye validaciones y total) ─────────────
    @rx.event
    def reset_filters_today(self):
        today = date.today().isoformat()
        self.start_date = today
        self.end_date = today
        self.status_filter = "TODOS"
        self.offset = 0
        self.set()

    @rx.event
    def load_transactions(self):
        # ── VALIDACIONES DE FECHA ───────────────────────────────────────────
        try:
            start_dt = date.fromisoformat(self.start_date)
            end_dt   = date.fromisoformat(self.end_date)
        except ValueError:
            yield rx.toast("Valor de fecha inválido")
            return

        if end_dt < start_dt:
            yield rx.toast("Párametros inválidos. Hasta no puede ser menor a Desde")
            return
        # ────────────────────────────────────────────────────────────────────

        txs = get_transactions_by_date_range_service(self.start_date, self.end_date)

        all_rows: List[Dict] = []
        total = 0
        for tx in txs:
            # filtro por estado
            if self.status_filter != "TODOS" and tx.status != self.status_filter:
                continue

            # username
            customer = select_by_id_service(tx.id_user)
            username = (
                f"{customer[0].username}"
                if customer and getattr(customer[0], "username", None)
                else str(tx.id_user)
            )

            # fila
            row = {
                "Usuario": username,
                "Observación": tx.observation or "",
                "Monto": tx.amount,
                "Fecha": tx.transaction_date.strftime("%Y-%m-%d %H:%M")
                if tx.transaction_date
                else "",
                "Estado": tx.status,
            }
            all_rows.append(row)
            total += tx.amount

        # guardamos todo
        self._all_rows = all_rows
        self.total_amount = total

        # paginación
        self.total_items = len(all_rows)
        self.offset = 0  # reinicia a la primera página
        yield self._refresh_page()


# ╭──────────────────────────────────────────────────────────────────────────────╮
# │                                UI Helpers                                   │
# ╰──────────────────────────────────────────────────────────────────────────────╯
def _title() -> rx.Component:
    return rx.text(
        "Transacciones",
        size="7",
        weight="bold",
        color="#3E2723",
        high_contrast=True,
        fontFamily="DejaVu Sans Mono",
        width="80%",
    )


def _filter_form() -> rx.Component:
    return rx.hstack(
        # ── Estado ───────────────────────────────────────────────────────────
        rx.text("Estado:", color="#3E2723"),
        rx.select(
            ["TODOS", "PAGO", "REVERSO", "GASTO"],
            value=TransactionView.status_filter,
            on_change=TransactionView.set_status,
            background_color="#3E2723",
            color="white",
        ),
        # ── Fechas ───────────────────────────────────────────────────────────
        rx.text("Desde:", color="#3E2723"),
        rx.input(
            type="date",
            value=TransactionView.start_date,
            on_change=TransactionView.set_start_date,
            background_color="#3E2723",
            color="white",
        ),
        rx.text("Hasta:", color="#3E2723"),
        rx.input(
            type="date",
            value=TransactionView.end_date,
            on_change=TransactionView.set_end_date,
            background_color="#3E2723",
            color="white",
        ),
        # ── Botón buscar ─────────────────────────────────────────────────────
        rx.button(
            rx.icon("search"),
            on_click=TransactionView.load_transactions,
            background_color="#3E2723",
            color="white",
            size="2",
            variant="solid",
        ),
        # ── Total global ─────────────────────────────────────────────────────
        rx.text("Total:", color="#3E2723"),
        rx.input(
            value=TransactionView.total_amount,
            read_only=True,
            disabled=True,
            background_color="#3E2723",
            color="white",
            width="100px",
            text_align="right",
        ),
        spacing="3",
        justify="center",
    )


def _table_header() -> rx.Component:
    return rx.table.row(
        *[rx.table.column_header_cell(col) for col in TABLE_COLUMNS],
        color="#3E2723",
        background_color="#A67B5B",
    )


def _table_body(tx: Dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(tx["Usuario"]),
        rx.table.cell(tx["Observación"]),
        rx.table.cell(tx["Monto"]),
        rx.table.cell(tx["Fecha"]),
        rx.table.cell(tx["Estado"]),
        color="#3E2723",
    )


def _pagination_controls() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("arrow-left", size=22),
            on_click=TransactionView.prev_page,
            is_disabled=TransactionView.offset <= 0,
            background_color="#3E2723",
            size="2",
            variant="solid",
        ),
        rx.text(
            TransactionView.current_page,
            " de ",
            TransactionView.num_total_pages,
            color="#3E2723",
        ),
        rx.button(
            rx.icon("arrow-right", size=22),
            on_click=TransactionView.next_page,
            is_disabled=TransactionView.offset + TransactionView.limit
            >= TransactionView.total_items,
            background_color="#3E2723",
            size="2",
            variant="solid",
        ),
        justify="center",
    )


@rx.page(on_load=[TransactionView.reset_filters_today, TransactionView.load_transactions])
def transactions() -> rx.Component:  # noqa: N802
    return rx.box(
        rx.vstack(
            _title(),
            _filter_form(),
            rx.table.root(
                rx.table.header(_table_header()),
                rx.table.body(rx.foreach(TransactionView.transactions, _table_body)),
                width="80vw",
                background_color="#FFF8E1",
                border_radius="20px",
            ),
            _pagination_controls(),
            spacing="5",
            align="center",
            width="80vw",
        ),
        display="flex",
        justify_content="center",
        align_items="flex-start",
        text_align="center",
        background_color="#FDEFEA",
        width="92vw",
        height="80vh",
    )
