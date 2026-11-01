
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://api.deadlock-api.com/v1/analytics/hero-stats"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def fetch_hero_stats():
    """Retrieve hero statistics from the Deadlock API."""
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Expected a list of hero statistics.")

    print(f"Successfully retrieved {len(data)} hero records.")
    return data


def save_hero_stats(data):
    """Save the API response as a timestamped JSON file."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_path = RAW_DATA_DIR / f"hero_stats_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Data saved to: {file_path}")


if __name__ == "__main__":
    hero_data = fetch_hero_stats()
    save_hero_stats(hero_data)
