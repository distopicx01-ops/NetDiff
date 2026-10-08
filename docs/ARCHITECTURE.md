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
    models/               -> tablas de la base de datos
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