def new_devices(old, new):
    """IPs que estan en el escaneo nuevo pero no en el viejo."""
    return sorted(ip for ip in new if ip not in old)

def removed_devices(old, new):
    """IPs que estaban antes y ya no aparecen."""
    return sorted(ip for ip in old if ip not in new)