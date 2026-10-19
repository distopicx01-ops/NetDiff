# NetDiff

NetDiff escanea tu red y te dice que cambio desde el ultimo escaneo:
dispositivos nuevos, dispositivos que desaparecieron y puertos que se abrieron o cerraron.
## Instalacion

Necesitas Python 3.13 y [nmap](https://nmap.org/download) instalado.

```
uv sync
```

## Uso

Corre los comandos desde la carpeta del proyecto:

```
python -m CLI.cli scan 192.168.1.0/24     # primer escaneo
python -m CLI.cli diff 192.168.1.0/24     # que cambio desde el ultimo
python -m CLI.cli deep 192.168.1.5        # versiones de servicios
python -m CLI.cli check 192.168.1.0/24    # puertos peligrosos
python -m CLI.cli whitelist add 192.168.1.1
python -m CLI.cli blacklist add 6.6.6.6
```

## Pruebas

```
python -m unittest discover -s tests -t .
```

La estructura del proyecto esta explicada en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
## Con Docker (demonio + API)

```
TARGET=192.168.1.0/24 INTERVAL=300 docker compose up -d --build
```

En PowerShell:

```
$env:TARGET="192.168.1.0/24"; $env:INTERVAL="300"; docker compose up -d --build
```

- `daemon` revisa la red cada `INTERVAL` segundos y guarda los cambios.
- `api` queda en http://localhost:8000 (documentacion en `/docs`).

| Endpoint | Que devuelve |
|---|---|
| `GET /health` | Si la API esta viva |
| `GET /status` | Resumen: equipos, eventos, ultimo escaneo |
| `GET /devices` | Equipos con puertos abiertos y sistema probable |
| `GET /devices/{ip}` | Un equipo con su historial |
| `GET /events?kind=new_device&limit=50` | Cambios detectados |
| `GET /operations` | Escaneos hechos por el demonio |
| `GET /snapshot/latest` | Ultima foto de la red |
| `GET /lists` | White list y black list |

Ver logs del demonio: `docker compose logs -f daemon`

> Nota: en Docker Desktop (Windows/Mac) el contenedor no ve tu red WiFi/LAN
> directamente. En Linux puedes agregar `network_mode: host` al servicio `daemon`
> para que escanee tu red real.