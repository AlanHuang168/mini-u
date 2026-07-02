# pipeline/cache.py
import json
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_key(ticker: str, mode: str = "full"):
    return f"{ticker}_{mode}"

def load_cache(ticker: str, mode: str = "full", expire_hours: int = 6):
    key = get_cache_key(ticker, mode)
    cache_file = CACHE_DIR / f"{key}.json"
    
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
            cached_time = datetime.fromisoformat(cache["timestamp"])
            if datetime.now() - cached_time < timedelta(hours=expire_hours):
                print(f"[Cache] 命中缓存: {ticker} ({mode})")
                return cache["data"]
        except:
            pass
    return None

def save_cache(ticker: str, data: dict, mode: str = "full"):
    key = get_cache_key(ticker, mode)
    cache_file = CACHE_DIR / f"{key}.json"
    
    cache = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"[Cache] 已保存缓存: {ticker} ({mode})")