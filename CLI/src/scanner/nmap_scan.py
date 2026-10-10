def parse_results(scanner):
    """Convierte lo que devuelve nmap en un diccionario simple.

    Resultado:
        {"192.168.1.5": {"hostname": "mi-pc", "ports": [22, 80]}}
    """
    devices = {}
    for ip in scanner.all_hosts():
        host = scanner[ip]
        ports = []
        for protocol in host.all_protocols():
            for port, info in host[protocol].items():
                if info["state"] == "open":
                    ports.append(port)
        devices[ip] = {"hostname": host.hostname(), "ports": sorted(ports)}
    return devices


def scan_network(target, arguments="-F"):
    """Escanea una red o una IP. "-F" es un escaneo rapido de puertos comunes."""
    import nmap  # se importa aqui para poder probar el resto sin nmap

    scanner = nmap.PortScanner()
    scanner.scan(hosts=target, arguments=arguments)
    return parse_results(scanner)