import reflex as rx
from datetime import date
from ..services.TransactionService import get_transactions_by_date_range_service

class TransactionView(rx.State):
    transactions: list = []
    start_date: str = date.today().isoformat()
    end_date: str = date.today().isoformat()

    @rx.event
    def set_start_date(self, value: str):
        self.start_date = value
        self.set()

    @rx.event
    def set_end_date(self, value: str):
        self.end_date = value
        self.set()

    @rx.event
    def load_transactions(self):
        transactions_obj = get_transactions_by_date_range_service(self.start_date, self.end_date)
        # Convertimos los objetos a dict para el data_table
        self.transactions = [
            {
                "id": tx.id,
                "observation": tx.observation or "",
                "amount": tx.amount,
                "transaction_date": tx.transaction_date.strftime('%Y-%m-%d %H:%M') if tx.transaction_date else "",
                "status": tx.status,
            }
            for tx in transactions_obj
        ]
        self.set()

def transactions():
    return rx.vstack(
        rx.heading("Transacciones", size="7", color="#3E2723"),
        rx.hstack(
            rx.text("Fecha desde:", size="4"),
            rx.input(
                type="date",
                value=TransactionView.start_date,
                on_change=TransactionView.set_start_date,
                background_color="#FDEFEA",
                color="#3E2723"
            ),
            rx.text("hasta", size="4"),
            rx.input(
                type="date",
                value=TransactionView.end_date,
                on_change=TransactionView.set_end_date,
                background_color="#FDEFEA",
                color="#3E2723"
            ),
            rx.button(
                "Buscar",
                on_click=TransactionView.load_transactions,
                background_color="#3E2723",
                color="white"
            ),
            spacing="3"
        ),
        rx.data_table(
            data=TransactionView.transactions,
            columns=["id", "observation", "amount", "transaction_date", "status"],
            headers=["ID", "Observación", "Monto", "Fecha", "Estado"],
            width="100%",
            pagination=True,
        ),
        spacing="6"
    )
