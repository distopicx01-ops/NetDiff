import argparse
import asyncio
import subprocess
import threading

from backend.daemon import detect_target, run_daemon_loop


def run_api():
    import uvicorn

    from backend.api import app

    print("[API] http://localhost:8000/docs", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")


def run_docker():
    check = subprocess.run(["docker", "info"], capture_output=True)
    if check.returncode != 0:
        print("Docker Desktop no esta abierto. Abrelo y vuelve a intentar.")
        return
    subprocess.run(["docker", "compose", "up", "-d", "--build"])


def run_local(target, interval, with_api):
    target = target or detect_target()
    print(f"Modo local | red: {target} | cada {interval or 'INTERVAL'}s")
    if with_api:
        threading.Thread(target=run_api, daemon=True).start()
    try:
        asyncio.run(run_daemon_loop(target=target, interval=interval))
    except KeyboardInterrupt:
        print("\nDetenido")


def main():
    parser = argparse.ArgumentParser(description="NetDiff: demonio + API")
    parser.add_argument("--docker", action="store_true", help="usar Docker Compose")
    parser.add_argument("--api-only", action="store_true", help="solo la API")
    parser.add_argument("--no-api", action="store_true", help="solo el demonio")
    parser.add_argument("--target", help="red a escanear, ej. 192.168.1.0/24")
    parser.add_argument("--interval", type=int, help="segundos entre escaneos")
    args = parser.parse_args()

    if args.docker:
        run_docker()
    elif args.api_only:
        run_api()
    else:
        run_local(args.target, args.interval, with_api=not args.no_api)


if __name__ == "__main__":
    main()
