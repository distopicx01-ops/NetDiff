# Arquitectura de NetDiff

```
NetDiff/
  CLI/                    -> lo que el usuario usa desde la terminal
    cli.py                -> lee los comandos (scan, diff, deep, check...)
    src/
      commands/           -> un archivo por comando
      scanner/            -> escaneo con nmap + comparar escaneos (diff)
      functions/
        deepScann/        -> escaneo profundo (versiones de servicios)
        pentesting/       -> revisa puertos peligrosos
      systems/            -> adivina el sistema operativo
  backend/
    models/               -> tablas de la base de datos (device, system,
                             operation, track, event)
    monitor.py            -> una revision: escanear, comparar y guardar
    daemon.py             -> el demonio: repite monitor.py cada INTERVAL segundos
    api.py                -> API (FastAPI) para consultar el estado
  Dockerfile              -> imagen con Python + nmap
  docker-compose.yml      -> levanta 2 servicios: daemon y api
  database/
    motor/eng.py          -> conexion a la base de datos (SQLAlchemy)
    init_db.py            -> crea las tablas
  tools/                  -> utilidades pequenas
    white-list/           -> IPs conocidas que se ignoran
    black-list/           -> IPs peligrosas que dan alerta
    keys/                 -> claves de acceso (se guardan con hash)
    users/                -> usuarios
    enterprises/          -> empresas
    storage.py            -> leer/guardar JSON
  systems/                -> datos para adivinar el sistema operativo
  src/netdiff/            -> punto de entrada del paquete (comando netdiff)
  tests/                  -> pruebas
```

## Flujo basico

1. `scan` escanea la red y guarda una "foto" (snapshot) en `data/snapshots`.
2. `diff` escanea otra vez y compara con la ultima foto.
3. `deep` busca versiones de servicios en un equipo.
4. `check` busca puertos peligrosos (telnet, ftp, rdp...).
## Demonio y API (Docker)

```
  docker-compose
   â”œâ”€ daemon  -> cada INTERVAL segundos: escanea TARGET, compara con la
   â”‚             ultima foto y guarda equipos y eventos en la base de datos
   â””â”€ api     -> lee la base de datos y responde por HTTP (puerto 8000)

   Los dos comparten el volumen "netdiff-data" (carpeta /app/data):
   data.db, snapshots/, white_list.json, black_list.json
```

Tipos de evento: `first_scan`, `new_device`, `removed_device`,
`ports_changed`, `blacklist_alert`.