from systems import OS_HINTS


def guess_os(ports):
    """Adivina el sistema operativo mirando los puertos abiertos."""
    for port in ports:
        if port in OS_HINTS:
            return OS_HINTS[port]
    return "Desconocido"