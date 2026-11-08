# --------------------------------------
# File: train_model.py
# Purpose: Read ML features and prepare datasets
# --------------------------------------

import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv  

# Locate the main project directory.
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Load database credentials.
load_dotenv(PROJECT_DIR / ".env")


def connect_db():
    """Connect to the PostgreSQL database."""

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "home_price_prediction"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )

def main():

    connection = connect_db()

    try:

        # Read the ML feature table from PostgreSQL.
        query = """
            SELECT *
            FROM ml_feature_table
            ORDER BY sale_id;
        """

        df = pd.read_sql_query(query, connection)

        print("ML FEATURE TABLE")
        print("=" * 50)
        print(f"Total records: {len(df)}")
            # Separate the data using the split column.
        train = df[df["split"] == "train"].copy()

        validate = df[df["split"] == "validate"].copy()

        test = df[df["split"] == "test"].copy()

        # Display the number of records in each dataset.
        print("\nDATASET SPLITS")
        print("=" * 50)

        print(f"Training records: {len(train)}")
        print(f"Validation records: {len(validate)}")
        print(f"Testing records: {len(test)}")

        # Check that none of the datasets are empty.
        if train.empty or validate.empty or test.empty:
            raise ValueError("One or more dataset splits are empty.")

        print("\nAll three datasets successfully loaded.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()