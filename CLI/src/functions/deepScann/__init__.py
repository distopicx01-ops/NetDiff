def parse_services(scanner):
    """Saca el servicio y version de cada puerto abierto.

    Resultado:
        {"192.168.1.5": {22: "ssh OpenSSH 8.9", 80: "http nginx 1.18"}}
    """
    result = {}
    for ip in scanner.all_hosts():
        host = scanner[ip]
        services = {}
        for protocol in host.all_protocols():
            for port, info in host[protocol].items():
                if info["state"] != "open":
                    continue
                text = f'{info.get("name", "")} {info.get("product", "")} {info.get("version", "")}'
                services[port] = " ".join(text.split())
        result[ip] = services
    return result

def deep_scan(target):
    """Escaneo profundo: "-sV" pregunta a cada puerto que programa usa."""
    import nmap

    scanner = nmap.PortScanner()
    scanner.scan(hosts=target, arguments="-sV")
    return parse_services(scanner)