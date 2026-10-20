# Arquitectura de NetDiff

```
NetDiff/
  CLI/                    -> comandos de terminal
    cli.py                -> lee los comandos (scan, diff, deep, check, listas)
    src/
      commands/           -> un archivo por comando
      scanner/
        nmap_scan.py      -> escaneo con python-nmap
        diff.py           -> compara dos escaneos
        snapshots.py      -> guarda/lee las "fotos" en data/snapshots
      functions/
        deepScann/        -> versiones de servicios (nmap -sV)
        pentesting/       -> revisa puertos peligrosos
      systems/            -> adivina el sistema operativo por los puertos
  backend/
    models/               -> tablas: device, event, operation, track, system, user
    schemas.py            -> modelos Pydantic (lo que entra y sale de la API)
    auth.py               -> passlib (hash de claves) + JWT (tokens)
    monitor.py            -> una revision: escanear, comparar y guardar
    daemon.py             -> bucle asyncio: repite monitor.py cada INTERVAL
    api.py                -> API FastAPI
  database/
    motor/eng.py          -> SQLAlchemy async + SQLite (aiosqlite)
    init_db.py            -> crea las tablas
  tools/                  -> utilidades pequenas
    white-list/           -> IPs conocidas que no dan aviso
    black-list/           -> IPs peligrosas que dan alerta
    keys/ users/ enterprises/
    storage.py            -> leer/guardar JSON
  systems/                -> tabla puerto -> sistema operativo
  src/netdiff/            -> punto de entrada (comando netdiff)
  scripts/scan.sh         -> escaneo rapido desde bash
  start.sh                -> arranque rapido desde bash
  modo_dual.py            -> demonio + API en un solo comando
  Dockerfile, docker-compose.yml
  tests/                  -> pruebas (unittest)
```

## Flujo del demonio

1. `daemon.py` llama a `run_check` cada `INTERVAL` segundos.
2. `run_check` escanea con nmap (en un hilo, para no bloquear asyncio).
3. Compara con la ultima foto y guarda equipos, puertos y eventos en SQLite.
4. `api.py` lee esa base de datos y responde por HTTP.

## Eventos

`first_scan`, `new_device`, `removed_device`, `ports_changed`, `blacklist_alert`.

## Seguridad de la API

- `POST /auth/register`: el primer usuario es `admin`, los demas `viewer`.
- `POST /auth/login`: devuelve un token JWT.
- `POST /scan`: solo admin. El `target` debe ser una IP o una red valida.
- El resto de consultas (`GET`) son publicas.
- Define `JWT_SECRET` en `.env`; si esta vacio se genera uno aleatorio en cada arranque.