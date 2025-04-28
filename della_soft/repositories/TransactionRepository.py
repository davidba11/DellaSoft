from ..models.TransactionModel import Transaction
from .ConnectDB import connect
from sqlmodel import Session

def insert_transaction(transaction: Transaction):
    engine = connect()
    with Session(engine) as session:
        session.add(transaction)
        session.commit()