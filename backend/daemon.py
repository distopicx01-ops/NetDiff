import os
import socket
import asyncio
from dotenv import load_dotenv
from backend.monitor import run_check
from database.motor.eng import init_db, AsyncSessionLocal

load_dotenv()

def detect_target():
    target_env = os.getenv('TARGET')
    if target_env:
        return target_env
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            octetos = local_ip.split('.')
            return f'{octetos[0]}.{octetos[1]}.{octetos[2]}.0/24'
    except Exception:
        return '127.0.0.1'

async def run_daemon_loop(target=None, interval=None):
    await init_db()
    target = target or detect_target()
    interval = int(interval or os.getenv('INTERVAL', '300'))
    print(f'=== NetDiff Demonio (Async) ===', flush=True)
    print(f'Red objetivo : {target}', flush=True)
    print(f'Frecuencia   : cada {interval} segundos', flush=True)
    ciclo = 1
    while True:
        print(f'[{ciclo}] Escaneando {target}...', flush=True)
        async with AsyncSessionLocal() as db:
            try:
                result = await run_check(db, target)
                print(f"    -> Nuevos: {len(result['new'])} | Quitados: {len(result['removed'])} | Puertos: {len(result['ports'])}", flush=True)
            except Exception as error:
                await db.rollback()
                print(f'    [!] Error en escaneo: {error}', flush=True)
        ciclo += 1
        await asyncio.sleep(interval)

def main():
    asyncio.run(run_daemon_loop())

if __name__ == '__main__':
    main()
