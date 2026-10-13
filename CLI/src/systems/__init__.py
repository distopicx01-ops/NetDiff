from collections import Counter

from systems import OS_HINTS


def guess_os(ports):
    """Adivina el sistema operativo mirando los puertos abiertos.

    Cada puerto "vota" por un sistema. Gana el que tenga mas votos.
    """
    votes = Counter(OS_HINTS[port] for port in ports if port in OS_HINTS)
    if not votes:
        return "Desconocido"
    return votes.most_common(1)[0][0]