import json
import os

def ensure_file(path, default_data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default_data, f, indent=2)

def read_json(path, default_data):
    ensure_file(path, default_data)
    with open(path, "r") as f:
        return json.load(f)

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
