import hashlib
import secrets

from tools.storage import read_json, write_json

DEFAULT_PATH = "data/keys.json"


def generate_key():
    """Crea una clave al azar."""
    return secrets.token_hex(16)


def hash_key(key):
    """Nunca guardamos la clave real, solo su hash."""
    return hashlib.sha256(key.encode()).hexdigest()


def save_key(name, key, path=DEFAULT_PATH):
    data = read_json(path, {})
    data[name] = hash_key(key)
    write_json(path, data)


def verify_key(name, key, path=DEFAULT_PATH):
    data = read_json(path, {})
    return data.get(name) == hash_key(key)