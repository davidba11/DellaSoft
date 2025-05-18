import asyncio
from datetime import datetime
from ..repositories.TransactionRepository import insert_transaction, select_transactions_by_date_range
from ..models.TransactionModel import Transaction

def create_transaction(transaction: Transaction):
    return insert_transaction(transaction)

def get_transactions_by_date_range_service(start_date: str, end_date: str):
    return select_transactions_by_date_range(start_date, end_date)