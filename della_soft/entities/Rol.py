from sqlmodel import SQLModel, Field, create_engine
import rxconfig as cf


class Rol(rx.Model, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    descripcion: str = Field(nullable=False)

engine = create_engine(cf.config.db_url, echo=True)

SQLModel.metadata.create_all(engine)