from sqlmodel import create_engine

def connect():
    return create_engine("postgresql://postgres:admin@localhost/DellaSoft")

