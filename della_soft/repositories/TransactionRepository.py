from datetime import datetime
from ..models.TransactionModel import Transaction
from .ConnectDB import connect
from sqlmodel import Session, select

def insert_transaction(transaction: Transaction):
    engine = connect()
    with Session(engine) as session:
        session.add(transaction)
        session.commit()


def select_transactions_by_date_range(start_date: str, end_date: str):
    engine = connect()
    with Session(engine) as session:
        query = select(Transaction).where(
            Transaction.transaction_date >= datetime.fromisoformat(start_date),
            Transaction.transaction_date <= datetime.fromisoformat(end_date)
        )
        return session.exec(query).all()
