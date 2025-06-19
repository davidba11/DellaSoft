import asyncio
from datetime import datetime
from ..models.POSModel import POS
from ..repositories.POSRepository import get_by_pos_date, insert_pos, update_pos

def pos_is_open(value: str):
    return get_by_pos_date(value)

def insert_pos_register(id: int, initial_amount: int, final_amount: int, pos_date: datetime):

    pos_save = POS(id=id, initial_amount=initial_amount, final_amount=final_amount, pos_date=pos_date)
    insert_pos(pos_save)

def update_final_amount(id: int, initial_amount: int, final_amount: int, pos_date: datetime):
    pos_update = POS(id=id, initial_amount=initial_amount, final_amount=final_amount, pos_date=pos_date)
    update_pos(pos_update)