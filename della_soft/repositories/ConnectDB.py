# della_soft/repositories/ConnectDB.py
import os
from urllib.parse import quote_plus

from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv

# Carga .env solo en local; en prod usa vars del sistema/CI
load_dotenv()

def _build_db_url() -> str:
    user = os.getenv("DB_USER", "postgres")
    pwd  = quote_plus(os.getenv("DB_PASSWORD", ""))
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "DellaSoft")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{name}"

def connect():
    engine = create_engine(_build_db_url(), echo=False)
    # En producción/migraciones usa Alembic, no create_all
    SQLModel.metadata.create_all(engine)
    return engine
