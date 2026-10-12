
from pathlib import Path
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

OUTPUT_FILE = Path("data/raw/census_ames_raw.json")

# Census ACS 5-year API: Ames city, Story County, Iowa.
URL = (
    "https://api.census.gov/data/2023/acs/acs5"
    "?get=NAME,B19013_001E,B01003_001E,B15003_022E"
    "&for=place:01855"
    "&in=state:19"
)


def main():
    api_key = os.getenv("CENSUS_API_KEY")

    if not api_key:
        raise ValueError("CENSUS_API_KEY is missing from your .env file.")

    response = requests.get(
        URL,
        params={"key": api_key},
        timeout=30,
    )
    if response.status_code != 200:
        print(f"HTTP status: {response.status_code}")
        print(f"Census API error: {response.text}")
        response.raise_for_status()

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("The Census API did not return valid JSON.")
        print(f"HTTP status: {response.status_code}")
        print(f"Response content: {response.text[:1000]}")
        raise

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

    print(f"Saved raw Census response to {OUTPUT_FILE}")
    print(f"Data rows returned: {max(len(data) - 1, 0)}")
    print(f"Fields returned: {data[0] if data else []}")


if __name__ == "__main__":
    main()
