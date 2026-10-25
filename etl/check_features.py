
# --------------------------------------
# File: check_features.py
# Purpose: Check the machine-learning feature data
# --------------------------------------

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
FEATURES_PATH = PROJECT_DIR / "data" / "clean" / "ml_features.csv"


def main():
    features = pd.read_csv(FEATURES_PATH)

    print("\nFEATURE TABLE OVERVIEW")
    print("=" * 50)
    print(f"Rows: {features.shape[0]}")
    print(f"Columns: {features.shape[1]}")

    print("\nCOLUMN DATA TYPES")
    print("-" * 50)
    print(features.dtypes)

    print("\nMISSING VALUES BY COLUMN")
    print("-" * 50)
    missing = features.isnull().sum()
    print(missing[missing > 0] if missing.any() else "No missing values found.")

    print("\nDUPLICATE SALE IDs")
    print("-" * 50)
    print(f"Duplicate sale IDs: {features['sale_id'].duplicated().sum()}")

    print("\nTARGET VARIABLE")
    print("-" * 50)
    print(features["sale_price"].describe())

    print("\nFEATURE CHECK COMPLETED.")


if __name__ == "__main__":
    main()
