from CLI.src.scanner.nmap_scan import get_scanner


def parse_services(scanner):
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
    scanner = get_scanner()
    scanner.scan(hosts=target, arguments="-sV")
    return parse_services(scanner)
