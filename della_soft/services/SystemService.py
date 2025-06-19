from datetime import datetime
import bcrypt

DATE_FMT_FULL   = "%d/%m/%Y %H:%M"
DATE_FMT_DAY    = "%d/%m/%Y"
ISO_FMT_LOCAL   = "%Y-%m-%dT%H:%M"
ISO_FMT_DB      = "%Y-%m-%d %H:%M:%S"

def get_sys_date_to_string():
    now_str = datetime.now().strftime(DATE_FMT_FULL)
    return now_str

def get_sys_date_to_string_two():
    now_str = datetime.now().strftime(DATE_FMT_DAY)
    return now_str

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def get_sys_date(date: str):
    formats = [
        ISO_FMT_LOCAL,     # ← input de <input type="datetime-local">
        ISO_FMT_DB,  # ← cuando viene de BD
        DATE_FMT_FULL,     # ← opcional, manual
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date, fmt)
        except ValueError:
            continue
    raise ValueError(f"Formato inválido para la fecha: {date}")

def get_sys_date_two(date: str):
    now_dt = datetime.strptime(date, DATE_FMT_DAY)
    return now_dt

def get_sys_date_three(date: str):
    date = date + " 00:00"
    now_dt = datetime.strptime(date, DATE_FMT_FULL)
    return now_dt