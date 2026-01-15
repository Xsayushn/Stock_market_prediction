from src.utils import read_json, write_json

WATCHLIST_FILE = "data/watchlist.json"

def get_watchlist(username: str):
    data = read_json(WATCHLIST_FILE, {})
    return data.get(username, [])

def add_to_watchlist(username: str, symbol: str):
    data = read_json(WATCHLIST_FILE, {})
    if username not in data:
        data[username] = []
    if symbol not in data[username]:
        data[username].append(symbol)
    write_json(WATCHLIST_FILE, data)

def remove_from_watchlist(username: str, symbol: str):
    data = read_json(WATCHLIST_FILE, {})
    if username in data and symbol in data[username]:
        data[username].remove(symbol)
    write_json(WATCHLIST_FILE, data)
