from tools.storage import read_json, write_json

DEFAULT_PATH = "data/enterprises.json"


def get_enterprises(path=DEFAULT_PATH):
    return read_json(path, [])


def add_enterprise(name, path=DEFAULT_PATH):
    items = get_enterprises(path)
    if name not in items:
        items.append(name)
        write_json(path, items)
    return items