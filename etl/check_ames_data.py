
from pathlib import Path

import pandas as pd

DATA_FILE = Path("data/manual/train.csv")

EXPECTED_COLUMNS = {
    "Id",
    "Neighborhood",
    "YrSold",
    "MoSold",
    "SalePrice",
    "OverallQual",
    "GrLivArea",
    "BedroomAbvGr",
    "FullBath",
    "YearBuilt",
    "GarageCars",
}


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {DATA_FILE}. "
            "Download the Kaggle Ames training file and save it there."
        )

    df = pd.read_csv(DATA_FILE)

    print(f"File: {DATA_FILE}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    missing = EXPECTED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(f"Required columns are missing: {sorted(missing)}")

    print("All required columns are present.")
    print("No data was modified or loaded into PostgreSQL.")


if __name__ == "__main__":
    main()
