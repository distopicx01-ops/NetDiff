import nmap


def get_scanner():
    try:
        return nmap.PortScanner()
    except nmap.PortScannerError as error:
        raise RuntimeError(
            "No se encontro el programa nmap. Instalalo desde https://nmap.org/download "
            "o usa Docker, que ya lo trae incluido."
        ) from error


def parse_results(scanner):
    devices = {}
    for ip in scanner.all_hosts():
        host = scanner[ip]
        if host.state() != "up":
            continue
        ports = []
        for protocol in host.all_protocols():
            for port, info in host[protocol].items():
                if info["state"] == "open":
                    ports.append(port)
        devices[ip] = {"hostname": host.hostname(), "ports": sorted(ports)}
    return devices


def scan_network(target, arguments="-F"):
    scanner = get_scanner()
    scanner.scan(hosts=target, arguments=arguments)
    return parse_results(scanner)
