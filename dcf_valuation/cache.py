import json
import os

CACHE_FILE = "api_cache.json"

def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_cached(key: str):
    cache = load_cache()
    return cache.get(key)

def set_cached(key: str, value):
    cache = load_cache()
    cache[key] = value
    save_cache(cache)