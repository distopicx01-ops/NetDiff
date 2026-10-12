import json
import os
from datetime import datetime

DEFAULT_FOLDER = "data/snapshots"


def save_snapshot(devices, folder=DEFAULT_FOLDER):
    """Guarda el escaneo en un archivo con la fecha en el nombre."""
    os.makedirs(folder, exist_ok=True)
    name = datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ".json"
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(devices, f, indent=2)
    return path