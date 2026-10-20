from collections import Counter
from systems import OS_HINTS

def guess_os(ports):
    votes = Counter((OS_HINTS[port] for port in ports if port in OS_HINTS))
    if not votes:
        return 'Desconocido'
    return votes.most_common(1)[0][0]
