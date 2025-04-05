from datetime import datetime

def get_sys_date_to_string():
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    return now_str

def get_sys_date(date: str):
    now_dt = datetime.strptime(date, "%d/%m/%Y %H:%M")
    return now_dt
