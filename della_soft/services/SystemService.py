from datetime import datetime
import bcrypt

def get_sys_date_to_string():
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    return now_str

def get_sys_date_to_string_two():
    now_str = datetime.now().strftime("%d/%m/%Y")
    return now_str

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def get_sys_date(date: str):
    now_dt = datetime.strptime(date, "%d/%m/%Y %H:%M")
    return now_dt

def get_sys_date_two(date: str):
    now_dt = datetime.strptime(date, "%d/%m/%Y")
    return now_dt

def get_sys_date_three(date: str):
    date = date + " 00:00"
    now_dt = datetime.strptime(date, "%d/%m/%Y %H:%M")
    return now_dt
