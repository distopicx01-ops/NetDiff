import argparse
import asyncio
import os
import subprocess
import threading
import time
from backend.daemon import detect_target, run_daemon_loop

def run_api_server():
    try:
        import uvicorn
        from backend.api import app
        print('--> [API] Iniciando en http://localhost:8000 (Docs: http://localhost:8000/docs)', flush=True)
        uvicorn.run(app, host='0.0.0.0', port=8000, log_level='warning')
    except Exception as e:
        print(f'[!] Error al iniciar la API: {e}', flush=True)

def check_docker_running():
    try:
        res = subprocess.run(['docker', 'info'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except Exception:
        return False

def start_docker_mode():
    print('=== MODO DOCKER ===')
    if not check_docker_running():
        print('[!] Docker Desktop no esta abierto o no responde.')
        return
    print('--> Levantando servicios con Docker Compose...')
    subprocess.run(['docker', 'compose', 'up', '-d', '--build'])

def start_local_mode(target=None, interval=None, start_api=True):
    print('==================================================')
    print('          NETDIFF - MODO DUAL (LOCAL)             ')
    print('==================================================')
    red = target or detect_target()
    segundos = interval or int(os.getenv('INTERVAL', '60'))
    print(f'[*] Red local detectada: {red}')
    print(f'[*] Intervalo de bucle : {segundos} segundos')
    if start_api:
        api_thread = threading.Thread(target=run_api_server, daemon=True)
        api_thread.start()
        time.sleep(1)
    print('\n[*] Activando bucle del demonio...\n')
    try:
        asyncio.run(run_daemon_loop(target=red, interval=segundos))
    except KeyboardInterrupt:
        print('\n[!] Bucle detenido.')

def main():
    parser = argparse.ArgumentParser(description='NetDiff - Lanzador Modo Dual')
    parser.add_argument('--docker', action='store_true', help='Arrancar con Docker Compose')
    parser.add_argument('--target', type=str, default=None, help='Red objetivo')
    parser.add_argument('--interval', type=int, default=None, help='Segundos entre escaneos')
    parser.add_argument('--no-api', action='store_true', help='No levantar la API')
    parser.add_argument('--api-only', action='store_true', help='Solo levantar la API')
    args = parser.parse_args()
    if args.docker:
        start_docker_mode()
    elif args.api_only:
        run_api_server()
    else:
        start_local_mode(target=args.target, interval=args.interval, start_api=not args.no_api)

if __name__ == '__main__':
    main()
