from CLI.src.functions.deepScann import deep_scan

def add_parser(sub):
    p = sub.add_parser('deep', help='Escaneo profundo: versiones de servicios')
    p.add_argument('target', help='Una IP, por ejemplo 192.168.1.5')
    p.set_defaults(func=run)

def run(args):
    result = deep_scan(args.target)
    for ip, services in result.items():
        print(ip)
        for port, text in services.items():
            print(f'  {port}: {text}')
