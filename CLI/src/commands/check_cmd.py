from CLI.src.functions.pentesting import check_risky_ports
from CLI.src.scanner.nmap_scan import scan_network


def add_parser(sub):
    p = sub.add_parser("check", help="Busca puertos peligrosos")
    p.add_argument("target", help="Ejemplo: 192.168.1.0/24")
    p.set_defaults(func=run)


def run(args):
    devices = scan_network(args.target)
    problems = check_risky_ports(devices)
    if not problems:
        print("No se encontraron puertos peligrosos")
        return
    for item in problems:
        print(f"{item['ip']}:{item['port']}  {item['reason']}")