import asyncio

from ..repositories.MeasureRepository import select_all, select_by_id

async def select_all_measure_service():
    measures = select_all()
    return measures

def select_name_by_id(measure_id: int) -> str:
    measure = select_by_id(measure_id)
    if measure:
        return f"{measure[0].description}"
    else:
        raise ValueError(f"No se encontró un cliente con ID {measure_id}")