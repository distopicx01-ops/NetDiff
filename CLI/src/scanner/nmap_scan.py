"""Escaneo de red.

Usa nmap si esta instalado. Si no esta instalado (por ejemplo en Windows
sin instalar nmap manualmente), usa un escaner nativo en Python con sockets.
"""
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import re
import socket
import subprocess

# Puertos mas frecuentes para revisar rapidamente si nmap no esta
FAST_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 3306, 3389, 5432, 5900, 8000, 8080]


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


def check_port(ip, port, timeout=0.15):
    """Prueba si un puerto especifico esta abierto."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((ip, port)) == 0
    except Exception:
        return False


def get_arp_ips():
    """Obtiene IPs conocidas en la red local usando la tabla ARP del sistema."""
    ips = set()
    try:
        output = subprocess.check_output(["arp", "-a"], text=True, stderr=subprocess.DEVNULL)
        for line in output.splitlines():
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            if match:
                ip = match.group(1)
                # Ignoramos broadcasts y multicast (ej. 255.255.255.255 o 224.0.0.x)
                if not ip.startswith(("224.", "239.", "255.")) and not ip.endswith(".255"):
                    ips.add(ip)
    except Exception:
        pass
    return ips


def scan_single_host(ip):
    """Escanea los puertos comunes de una IP y obtiene su hostname si responde."""
    open_ports = []
    for port in FAST_PORTS:
        if check_port(ip, port):
            open_ports.append(port)

    # Si encontramos puertos abiertos o la IP viene de ARP / ping
    hostname = ""
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except Exception:
        pass

    return ip, hostname, open_ports


def native_scan(target):
    """Escaneo simple y rapido en Python puro cuando nmap no esta en el sistema."""
    target_ips = []

    # Determinar si el target es una sola IP o una subred (ej. 192.168.1.0/24)
    if "/" in target:
        try:
            net = ipaddress.ip_network(target, strict=False)
            # Primero incluimos las IPs de la tabla ARP que caigan en la red
            arp_ips = {ip for ip in get_arp_ips() if ipaddress.ip_address(ip) in net}
            target_ips = list(arp_ips)
            # Si hay pocas o ninguna, probamos un barrido de hosts
            if len(target_ips) <= 1:
                target_ips = [str(ip) for ip in list(net.hosts())[:64]]
        except Exception:
            target_ips = [target.split("/")[0]]
    else:
        target_ips = [target]

    devices = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(scan_single_host, target_ips)
        for ip, hostname, ports in results:
            # Si tiene puertos abiertos o respondio en ARP, lo incluimos
            if ports or ip in get_arp_ips() or "/" not in target:
                devices[ip] = {
                    "hostname": hostname,
                    "ports": sorted(ports),
                }

    return devices


def scan_network(target, arguments="-F"):
    """Escanea una red o una IP.

    Usa nmap primero. Si nmap no esta instalado en PATH, usa native_scan.
    """
    try:
        import nmap
        scanner = nmap.PortScanner()
        scanner.scan(hosts=target, arguments=arguments)
        return parse_results(scanner)
    except Exception:
        # Fallback automatico para que funcione sin instalar nmap manualmente
        return native_scan(target)