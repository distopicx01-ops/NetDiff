# NetDiff

NetDiff escanea tu red con nmap y te dice que cambio desde el ultimo escaneo:
equipos nuevos, equipos que desaparecieron y puertos que se abrieron o cerraron.

Stack: Python, python-nmap, SQLAlchemy (async) + SQLite, FastAPI, Pydantic,
JWT + passlib, asyncio, dotenv, bash y Docker.

## Instalacion

Necesitas Python 3.13 y [nmap](https://nmap.org/download) instalado (Docker ya lo trae).

```
uv sync
copy .env.example .env
```

## Comandos de terminal

```
python -m CLI.cli scan 192.168.1.0/24
python -m CLI.cli diff 192.168.1.0/24
python -m CLI.cli deep 192.168.1.5
python -m CLI.cli check 192.168.1.0/24
python -m CLI.cli whitelist add 192.168.1.1
python -m CLI.cli blacklist add 6.6.6.6
```

## Demonio + API

Local (necesita nmap en tu PC):

```
python modo_dual.py                          # autodetecta tu red
python modo_dual.py --target 192.168.1.0/24 --interval 60
```

O con el script bash: `./start.sh`, `./start.sh daemon`, `./start.sh api`, `./start.sh test`.

Docker:

```
$env:TARGET="192.168.1.0/24"; $env:INTERVAL="300"; $env:JWT_SECRET="cambia-esto-por-algo-largo-y-secreto"
docker compose up -d --build
docker compose logs -f daemon
```

> En Docker Desktop (Windows/Mac) el contenedor no ve tu WiFi/LAN. En Linux agrega
> `network_mode: host` al servicio `daemon` para escanear tu red real.

La API queda en http://localhost:8000/docs

| Endpoint | Que hace |
|---|---|
| `GET /health` | La API esta viva |
| `GET /status` | Resumen: equipos, eventos, ultimo escaneo |
| `GET /devices`, `GET /devices/{ip}` | Equipos y su historial |
| `GET /events?kind=new_device&limit=50` | Cambios detectados |
| `GET /operations` | Escaneos hechos |
| `GET /snapshot/latest`, `GET /lists` | Ultima foto y listas |
| `POST /auth/register`, `POST /auth/login` | Usuarios y token JWT (el primero es admin) |
| `POST /scan` | Escanea ahora (solo admin, con token) |

## Pruebas

```
python -m unittest discover -s tests -t .
```

La estructura esta explicada en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).