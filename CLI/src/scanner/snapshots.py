import json
import os
from datetime import datetime
DEFAULT_FOLDER = 'data/snapshots'

def save_snapshot(devices, folder=DEFAULT_FOLDER):
    os.makedirs(folder, exist_ok=True)
    name = datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.json'
    path = os.path.join(folder, name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(devices, f, indent=2)
    return path

def load_latest_snapshot(folder=DEFAULT_FOLDER):
    if not os.path.isdir(folder):
        return None
    files = sorted((f for f in os.listdir(folder) if f.endswith('.json')))
    if not files:
        return None
    with open(os.path.join(folder, files[-1]), encoding='utf-8') as f:
        return json.load(f)
