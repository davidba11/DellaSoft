from datetime import datetime, timedelta
from ..models.TransactionModel import Transaction
from .ConnectDB import connect
from sqlmodel import Session, select

def insert_transaction(transaction: Transaction):
    engine = connect()
    with Session(engine) as session:
        session.add(transaction)
        session.commit()


def select_transactions_by_date_range(start_date: str, end_date: str):
    
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date) + timedelta(days=1) - timedelta(microseconds=1)

    engine = connect()
    with Session(engine) as session:
        query = (
            select(Transaction)
            .where(Transaction.transaction_date >= start_dt)
            .where(Transaction.transaction_date <= end_dt)
        )
        return session.exec(query).all()
