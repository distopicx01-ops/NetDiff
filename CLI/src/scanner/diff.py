def new_devices(old, new):
    return sorted((ip for ip in new if ip not in old))

def removed_devices(old, new):
    return sorted((ip for ip in old if ip not in new))

def changed_ports(old, new):
    changes = {}
    for ip in new:
        if ip not in old:
            continue
        before = set(old[ip]['ports'])
        after = set(new[ip]['ports'])
        opened = sorted(after - before)
        closed = sorted(before - after)
        if opened or closed:
            changes[ip] = {'opened': opened, 'closed': closed}
    return changes

def compare_scans(old, new):
    return {'new': new_devices(old, new), 'removed': removed_devices(old, new), 'ports': changed_ports(old, new)}
