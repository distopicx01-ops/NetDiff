from backend.models import device, operation, system, track
from database.motor.eng import Base, engine

def init_db():
    Base.metadata.create_all(engine)
if __name__ == '__main__':
    init_db()
    print('Tablas creadas')
