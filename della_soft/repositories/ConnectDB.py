# della_soft/repositories/ConnectDB.py
import os
from sqlmodel import create_engine, SQLModel
from dotenv import load_dotenv   # pip install python-dotenv

load_dotenv()  # lee .env si existe

def connect():
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "DellaSoft")

    if not (db_user and db_pass):
        raise RuntimeError(
            "Variables DB_USER y/o DB_PASSWORD no están definidas. "
            "Agrégalas a tu entorno o al archivo .env."
        )

    url = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(url, pool_pre_ping=True, echo=False)

    # ⚠️ crea tablas solo en desarrollo
    if os.getenv("ENV", "dev") == "dev":
        SQLModel.metadata.create_all(engine)

    return engine
