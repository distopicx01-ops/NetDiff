def new_devices(old, new):
    """IPs que estan en el escaneo nuevo pero no en el viejo."""
    return sorted(ip for ip in new if ip not in old)

def removed_devices(old, new):
    """IPs que estaban antes y ya no aparecen."""
    return sorted(ip for ip in old if ip not in new)

def changed_ports(old, new):
    """Puertos que se abrieron o cerraron en equipos que siguen en la red."""
    changes = {}
    for ip in new:
        if ip not in old:
            continue
        before = set(old[ip]["ports"])
        after = set(new[ip]["ports"])
        opened = sorted(after - before)
        closed = sorted(before - after)
        if opened or closed:
            changes[ip] = {"opened": opened, "closed": closed}
    return changes