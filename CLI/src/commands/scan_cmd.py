from CLI.src.scanner.nmap_scan import scan_network
from CLI.src.scanner.snapshots import save_snapshot
from CLI.src.systems import guess_os


def add_parser(sub):
    p = sub.add_parser("scan", help="Escanea la red y guarda una foto")
    p.add_argument("target", help="Ejemplo: 192.168.1.0/24")
    p.set_defaults(func=run)


def run(args):
    devices = scan_network(args.target)
    path = save_snapshot(devices)
    print(f"Se encontraron {len(devices)} dispositivos")
    for ip, info in devices.items():
        print(f"  {ip}  {info['hostname']}  puertos={info['ports']}  so={guess_os(info['ports'])}")
    print(f"Guardado en {path}")