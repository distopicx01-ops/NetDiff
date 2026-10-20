from CLI.src.scanner.diff import compare_scans
from CLI.src.scanner.nmap_scan import scan_network
from CLI.src.scanner.snapshots import load_latest_snapshot, save_snapshot
from tools import load

def add_parser(sub):
    p = sub.add_parser('diff', help='Compara la red con el ultimo escaneo')
    p.add_argument('target', help='Ejemplo: 192.168.1.0/24')
    p.set_defaults(func=run)

def run(args):
    white = load('white-list')
    black = load('black-list')
    old = load_latest_snapshot()
    new = scan_network(args.target)
    save_snapshot(new)
    if old is None:
        print('No habia un escaneo anterior. Este es el primero.')
        return
    result = compare_scans(old, new)
    known = white.get_all()
    new_ips = [ip for ip in result['new'] if ip not in known]
    print(f'Dispositivos nuevos: {len(new_ips)}')
    for ip in new_ips:
        print(f"  + {ip} {new[ip]['hostname']}")
        if black.contains(ip):
            print('    ALERTA: esta IP esta en la lista negra')
    print(f"Dispositivos que ya no estan: {len(result['removed'])}")
    for ip in result['removed']:
        print(f'  - {ip}')
    print(f"Cambios de puertos: {len(result['ports'])}")
    for ip, change in result['ports'].items():
        print(f"  * {ip} abiertos={change['opened']} cerrados={change['closed']}")
