import asyncio
from datetime import datetime
from ..repositories.TransactionRepository import insert_transaction
from ..models.TransactionModel import Transaction

def create_transaction(transaction: Transaction):
    return insert_transaction(transaction)