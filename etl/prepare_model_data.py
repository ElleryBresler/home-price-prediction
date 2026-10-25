
# --------------------------------------
# File: prepare_model_data.py
# Purpose: Prepare data for home-price modeling
# --------------------------------------

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
FEATURES_PATH = PROJECT_DIR / "data" / "clean" / "ml_features.csv"
OUTPUT_DIR = PROJECT_DIR / "data" / "clean"


def main():
    # Load the feature table created from PostgreSQL.
    data = pd.read_csv(FEATURES_PATH)

    # Sort by sale date.
    data = data.sort_values(
        ["sale_year", "sale_month", "sale_id"]
    ).reset_index(drop=True)

    # Split by complete years to prevent years from crossing sets.
    train = data[data["sale_year"] <= 2008].copy()
    validation = data[data["sale_year"] == 2009].copy()
    test = data[data["sale_year"] == 2010].copy()

    # Separate predictors from the target variable.
    # sale_id is an identifier; sale_price is what we predict.
    excluded_columns = ["sale_id", "sale_price"]

    X_train = train.drop(columns=excluded_columns)
    y_train = train["sale_price"]

    X_validation = validation.drop(columns=excluded_columns)
    y_validation = validation["sale_price"]

    X_test = test.drop(columns=excluded_columns)
    y_test = test["sale_price"]

    # Encode neighborhood as numeric indicator columns.
    X_train = pd.get_dummies(
        X_train, columns=["neighborhood"], dtype=int
    )
    X_validation = pd.get_dummies(
        X_validation, columns=["neighborhood"], dtype=int
    )
    X_test = pd.get_dummies(
        X_test, columns=["neighborhood"], dtype=int
    )

    # Keep identical predictor columns across all datasets.
    X_validation = X_validation.reindex(
        columns=X_train.columns, fill_value=0
    )
    X_test = X_test.reindex(
        columns=X_train.columns, fill_value=0
    )

    # Save each split separately.
    X_train.to_csv(OUTPUT_DIR / "X_train.csv", index=False)
    y_train.to_frame(name="sale_price").to_csv(
        OUTPUT_DIR / "y_train.csv", index=False
    )

    X_validation.to_csv(
        OUTPUT_DIR / "X_validation.csv", index=False
    )
    y_validation.to_frame(name="sale_price").to_csv(
        OUTPUT_DIR / "y_validation.csv", index=False
    )

    X_test.to_csv(OUTPUT_DIR / "X_test.csv", index=False)
    y_test.to_frame(name="sale_price").to_csv(
        OUTPUT_DIR / "y_test.csv", index=False
    )

    print("\nMODELING DATA PREPARATION")
    print("=" * 50)
    print(f"Total records: {len(data)}")
    print(f"Training records: {len(X_train)}")
    print(f"Validation records: {len(X_validation)}")
    print(f"Test records: {len(X_test)}")
    print(f"Predictor columns: {X_train.shape[1]}")

    print("\nSale-year ranges:")
    print(
        "Training:",
        train["sale_year"].min(),
        "to",
        train["sale_year"].max(),
    )
    print(
        "Validation:",
        validation["sale_year"].min(),
        "to",
        validation["sale_year"].max(),
    )
    print(
        "Test:",
        test["sale_year"].min(),
        "to",
        test["sale_year"].max(),
    )

    print("\nSaved training, validation, and test files.")
    print("Model data preparation completed.")


if __name__ == "__main__":
    main()
