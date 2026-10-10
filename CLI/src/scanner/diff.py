def new_devices(old, new):
    """IPs que estan en el escaneo nuevo pero no en el viejo."""
    return sorted(ip for ip in new if ip not in old)