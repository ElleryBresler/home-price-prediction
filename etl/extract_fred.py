
from pathlib import Path
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

OUTPUT_FILE = Path("data/raw/fred_mortgage_raw.json")
URL = "https://api.stlouisfed.org/fred/series/observations"


def main():
    api_key = os.getenv("FRED_API_KEY")

    if not api_key:
        raise ValueError("FRED_API_KEY is missing from your .env file.")

    params = {
        "series_id": "MORTGAGE30US",
        "api_key": api_key,
        "file_type": "json",
        "observation_start": "2006-01-01",
    }

    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    observations = data.get("observations", [])

    print(f"Saved raw FRED response to {OUTPUT_FILE}")
    print(f"Observations returned: {len(observations)}")


if __name__ == "__main__":
    main()
