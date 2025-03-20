from sqlmodel import create_engine, SQLModel

def connect():
    engine = create_engine("postgresql://postgres:admin@localhost/DellaSoft")
    SQLModel.metadata.create_all(engine)
    return engine

