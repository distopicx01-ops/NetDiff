"""Script Modo Dual para NetDiff.

Te permite correr NetDiff de 2 formas:
1. MODO LOCAL (recomendado en Windows):
   Corre el demonio en bucle directamente en tu red WiFi/cable,
   y levanta la API en http://localhost:8000 para ver todo.
   No necesita Docker Desktop prendido.

2. MODO DOCKER:
   Levanta los contenedores en segundo plano usando Docker Compose.
   (Requiere tener abierta la aplicacion Docker Desktop).

Uso:
    python modo_dual.py          -> Inicia en Modo Local (bucle + API)
    python modo_dual.py --docker -> Inicia con Docker Compose
    python modo_dual.py --api    -> Solo levanta la API web
"""
import argparse
import os
import subprocess
import sys
import threading
import time

from backend.daemon import detect_target, run_daemon_loop


def run_api_server():
    """Inicia el servidor web FastAPI con uvicorn en un hilo separado."""
    try:
        import uvicorn
        from backend.api import app

        print("--> [API] Iniciando en http://localhost:8000 (Docs: http://localhost:8000/docs)", flush=True)
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
    except Exception as e:
        print(f"[!] No se pudo iniciar la API: {e}", flush=True)


def check_docker_running():
    """Comprueba si el servicio Docker Desktop esta abierto."""
    try:
        res = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except Exception:
        return False


def start_docker_mode():
    """Modo Docker: levanta los contenedores con docker compose."""
    print("=== MODO DOCKER ===")
    if not check_docker_running():
        print("[!] Docker Desktop no esta abierto o no responde.")
        print("    Abre la aplicacion 'Docker Desktop' en Windows y vuelve a intentarlo.")
        print("    O bien, usa el Modo Local corriendo: python modo_dual.py")
        return

    print("--> Levantando servicios con Docker Compose...")
    cmd = ["docker", "compose", "up", "-d", "--build"]
    ret = subprocess.run(cmd)
    if ret.returncode == 0:
        print("\n[OK] NetDiff esta corriendo en Docker:")
        print("     - API disponible en: http://localhost:8000/docs")
        print("     - Ver logs del demonio: docker compose logs -f daemon")
        print("     - Detener todo: docker compose down")


def start_local_mode(target=None, interval=None, start_api=True):
    """Modo Local: corre en Windows directo sin Docker."""
    print("==================================================")
    print("          NETDIFF - MODO DUAL (LOCAL)             ")
    print("==================================================")

    red = target or detect_target()
    segundos = interval or int(os.getenv("INTERVAL", "60"))

    print(f"[*] Red local detectada: {red}")
    print(f"[*] Intervalo de bucle : {segundos} segundos")

    if start_api:
        # Iniciamos la API en un hilo de fondo para que el bucle siga en consola
        api_thread = threading.Thread(target=run_api_server, daemon=True)
        api_thread.start()
        time.sleep(1)

    print("\n[*] Activando bucle del demonio...\n")
    try:
        run_daemon_loop(target=red, interval=segundos)
    except KeyboardInterrupt:
        print("\n[!] Bucle detenido por el usuario.")


def main():
    parser = argparse.ArgumentParser(description="NetDiff - Lanzador Modo Dual")
    parser.add_argument("--docker", action="store_true", help="Arrancar en Modo Docker (Docker Compose)")
    parser.add_argument("--target", type=str, default=None, help="Red objetivo (ej. 192.168.1.0/24)")
    parser.add_argument("--interval", type=int, default=None, help="Segundos entre cada escaneo")
    parser.add_argument("--no-api", action="store_true", help="No levantar el servidor web de la API")
    parser.add_argument("--api-only", action="store_true", help="Solo levantar la API web")

    args = parser.parse_args()

    if args.docker:
        start_docker_mode()
    elif args.api_only:
        run_api_server()
    else:
        start_local_mode(target=args.target, interval=args.interval, start_api=not args.no_api)


if __name__ == "__main__":
    main()
