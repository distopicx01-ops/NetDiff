from tools.storage import read_json, write_json

DEFAULT_PATH = "data/white_list.json"


def get_all(path=DEFAULT_PATH):
    """Lista de IPs conocidas (se ignoran en el diff)."""
    return read_json(path, [])


def add(ip, path=DEFAULT_PATH):
    items = get_all(path)
    if ip not in items:
        items.append(ip)
        write_json(path, items)
    return items