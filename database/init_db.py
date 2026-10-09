"""Crea las tablas en la base de datos.

Uso:  python -m database.init_db
"""
from backend.models import device, operation, system, track  # noqa: F401
from database.motor.eng import Base, engine


def init_db():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("Tablas creadas")