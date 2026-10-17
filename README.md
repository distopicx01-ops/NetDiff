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