import asyncio
from ..models.POSModel import POS
from ..repositories.POSRepository import get_by_pos_date

def POS_is_open(value: str):
    return get_by_pos_date(value)