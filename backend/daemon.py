"""El demonio: cada cierto tiempo revisa la red y guarda los cambios.

Variables de entorno:
    TARGET    red a escanear           (ej. 192.168.1.0/24)
    INTERVAL  segundos entre revisiones (por defecto 300)
"""
import os
import time

from backend.monitor import run_check
from database.init_db import init_db
from database.motor.eng import SessionLocal

TARGET = os.getenv("TARGET", "127.0.0.1")
INTERVAL = int(os.getenv("INTERVAL", "300"))


def main():
    init_db()
    print(f"[daemon] vigilando {TARGET} cada {INTERVAL}s", flush=True)
    while True:
        db = SessionLocal()
        try:
            result = run_check(db, TARGET)
            print(
                f"[daemon] nuevos={len(result['new'])} "
                f"quitados={len(result['removed'])} "
                f"puertos={len(result['ports'])}",
                flush=True,
            )
        except Exception as error:  # el demonio no se debe caer por un error
            db.rollback()
            print(f"[daemon] error: {error}", flush=True)
        finally:
            db.close()
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
