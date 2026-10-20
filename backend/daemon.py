"""El demonio: cada cierto tiempo revisa la red y guarda los cambios.

Variables de entorno opcionales:
    TARGET    red a escanear (ej. 192.168.1.0/24). Si no se define, se autodetecta.
    INTERVAL  segundos entre revisiones (por defecto 300 segundos, o 60 para pruebas)
"""
import os
import socket
import time

from backend.monitor import run_check
from database.init_db import init_db
from database.motor.eng import SessionLocal


def detect_target():
    """Si el usuario no paso TARGET, detectamos la red local de esta maquina."""
    target_env = os.getenv("TARGET")
    if target_env:
        return target_env

    try:
        # Abre un socket dummy para saber que IP local tiene esta maquina
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            # Convertimos ej: 10.0.0.38 a 10.0.0.0/24
            octetos = local_ip.split(".")
            return f"{octetos[0]}.{octetos[1]}.{octetos[2]}.0/24"
    except Exception:
        return "127.0.0.1"


def run_daemon_loop(target=None, interval=None):
    """Ejecuta el bucle continuo del demonio."""
    init_db()

    target = target or detect_target()
    interval = int(interval or os.getenv("INTERVAL", "300"))

    print(f"=== NetDiff Demonio ===", flush=True)
    print(f"Red objetivo : {target}", flush=True)
    print(f"Frecuencia   : cada {interval} segundos", flush=True)
    print(f"Presiona Ctrl+C para detener.\n", flush=True)

    ciclo = 1
    while True:
        print(f"[{ciclo}] Iniciando escaneo de {target}...", flush=True)
        db = SessionLocal()
        try:
            result = run_check(db, target)
            print(
                f"    -> Nuevos: {len(result['new'])} | "
                f"Desconectados: {len(result['removed'])} | "
                f"Cambios de puertos: {len(result['ports'])}",
                flush=True,
            )
            for ip in result["new"]:
                print(f"       + Nuevo equipo detectado: {ip}", flush=True)
            for ip in result["removed"]:
                print(f"       - Equipo ya no responde: {ip}", flush=True)
            for ip, pinfo in result["ports"].items():
                print(f"       * Puertos cambiados en {ip}: {pinfo}", flush=True)
        except Exception as error:
            db.rollback()
            print(f"    [!] Error en escaneo: {error}", flush=True)
        finally:
            db.close()

        print(f"    Esperando {interval} segundos para la siguiente vuelta...\n", flush=True)
        ciclo += 1
        time.sleep(interval)


def main():
    run_daemon_loop()


if __name__ == "__main__":
    main()
