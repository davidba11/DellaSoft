from datetime import datetime
import bcrypt

def get_sys_date_to_string():

    now_str=datetime.now().strftime("%d/%m/%Y %H:%M")
    return now_str

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))