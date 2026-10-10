import json
import os


def read_json(path, default):
    """Lee un archivo JSON. Si no existe devuelve el valor por defecto."""
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    """Guarda datos en un archivo JSON (crea la carpeta si hace falta)."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)