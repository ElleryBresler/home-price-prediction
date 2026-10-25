
# --------------------------------------
# File: load.py
# Purpose: Load clean CSV files into PostgreSQL
# --------------------------------------

import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv


# Find the project root, regardless of the current terminal directory.
PROJECT_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = PROJECT_DIR / "data" / "clean"

# Load database settings from the project's .env file.
load_dotenv(PROJECT_DIR / ".env")


# CSV filename, database table, and insert columns.
TABLES = [
    (
        "dim_property.csv",
        "dim_property",
        [
            "property_id",
            "overall_qual",
            "gr_liv_area",
            "bedroom_abvgr",
            "full_bath",
            "year_built",
            "garage_cars",
        ],
    ),
    (
        "dim_location.csv",
        "dim_location",
        [
            "location_id",
            "neighborhood",
            "city",
            "county",
            "state",
            "median_household_income",
            "population",
            "bachelors_degree_count",
        ],
    ),
    (
        "dim_date.csv",
        "dim_date",
        [
            "date_id",
            "sale_year",
            "sale_month",
            "sale_quarter",
        ],
    ),
    (
        "fact_economic_conditions.csv",
        "fact_economic_conditions",
        [
            "date_id",
            "mortgage_rate",
        ],
    ),
    (
        "fact_home_sale.csv",
        "fact_home_sale",
        [
            "sale_id",
            "property_id",
            "location_id",
            "date_id",
            "sale_price",
        ],
    ),
]


def connect_db():
    """Connect using either DB_* or PG* variables from .env."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST") or os.getenv("PGHOST", "localhost"),
        port=os.getenv("DB_PORT") or os.getenv("PGPORT", "5432"),
        dbname=os.getenv("DB_NAME") or os.getenv(
            "PGDATABASE", "home_price_prediction"
        ),
        user=os.getenv("DB_USER") or os.getenv("PGUSER", "postgres"),
        password=os.getenv("DB_PASSWORD") or os.getenv("PGPASSWORD"),
    )


def main():
    connection = None

    try:
        connection = connect_db()

        # A transaction rolls back the load if something fails.
        with connection:
            with connection.cursor() as cursor:

                # Confirm the connection points to the expected database
                # and that the required tables already exist.
                cursor.execute("SELECT current_database();")
                database_name = cursor.fetchone()[0]
                print(f"Connected to database: {database_name}")

                required_tables = [
                    "dim_property",
                    "dim_location",
                    "dim_date",
                    "fact_economic_conditions",
                    "fact_home_sale",
                ]

                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_type = 'BASE TABLE';
                """)
                existing_tables = {row[0] for row in cursor.fetchall()}

                missing_tables = [
                    table for table in required_tables
                    if table not in existing_tables
                ]

                if missing_tables:
                    raise RuntimeError(
                        "Required tables do not exist in database "
                        f"'{database_name}': {missing_tables}. "
                        "Initialize the database schema before loading data."
                    )

                # Clear existing rows so rerunning the loader
                # replaces the data instead of duplicating it.
                cursor.execute("""
                    TRUNCATE TABLE
                        fact_home_sale,
                        fact_economic_conditions,
                        dim_property,
                        dim_location,
                        dim_date
                    RESTART IDENTITY CASCADE;
                """)

                # Load dimension tables before fact tables.
                for filename, table_name, columns in TABLES:
                    file_path = CLEAN_DIR / filename

                    if not file_path.exists():
                        raise FileNotFoundError(
                            f"Required CSV not found: {file_path}"
                        )

                    df = pd.read_csv(file_path)

                    # Confirm that the CSV has the expected columns.
                    missing_columns = [
                        column for column in columns
                        if column not in df.columns
                    ]

                    if missing_columns:
                        raise ValueError(
                            f"{filename} is missing columns: "
                            f"{missing_columns}"
                        )

                    # Convert pandas missing values to Python None,
                    # which PostgreSQL stores as NULL.
                    df = df[columns].astype(object)
                    df = df.where(pd.notna(df), None)

                    column_sql = ", ".join(columns)
                    placeholders = ", ".join(
                        ["%s"] * len(columns)
                    )

                    insert_sql = (
                        f"INSERT INTO {table_name} "
                        f"({column_sql}) "
                        f"VALUES ({placeholders})"
                    )

                    rows = list(df.itertuples(index=False, name=None))

                    if rows:
                        cursor.executemany(insert_sql, rows)

                    print(f"Loaded {table_name}: {len(rows)} rows")

        print("\nDatabase load completed successfully.")

    except Exception as error:
        print(f"\nDatabase load failed: {error}")
        raise

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
