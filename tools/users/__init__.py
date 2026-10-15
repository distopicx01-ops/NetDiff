from tools.storage import read_json, write_json

DEFAULT_PATH = "data/users.json"


def get_users(path=DEFAULT_PATH):
    return read_json(path, {})


def add_user(name, role="viewer", path=DEFAULT_PATH):
    """Agrega un usuario. Roles simples: admin o viewer."""
    users = get_users(path)
    users[name] = {"role": role}
    write_json(path, users)
    return users[name]


def find_user(name, path=DEFAULT_PATH):
    return get_users(path).get(name)