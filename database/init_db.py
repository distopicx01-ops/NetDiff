import asyncio
from database.motor.eng import init_db

if __name__ == '__main__':
    asyncio.run(init_db())
    print('Tablas creadas')
