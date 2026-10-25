
# --------------------------------------
# File: init_housing_schema.py
# Purpose: Safely create housing-project tables
# --------------------------------------

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


def main():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST") or os.getenv("PGHOST", "localhost"),
        port=os.getenv("DB_PORT") or os.getenv("PGPORT", "5432"),
        dbname=os.getenv("DB_NAME") or os.getenv(
            "PGDATABASE", "home_price_prediction"
        ),
        user=os.getenv("DB_USER") or os.getenv("PGUSER", "postgres"),
        password=os.getenv("DB_PASSWORD") or os.getenv("PGPASSWORD"),
    )

    schema_sql = (PROJECT_DIR / "sql" / "schema.sql").read_text(
        encoding="utf-8"
    )

    # Refuse to run a schema containing destructive DROP statements.
    if "DROP TABLE" in schema_sql.upper():
        raise RuntimeError(
            "schema.sql contains DROP TABLE statements. "
            "No changes were made. Create a non-destructive schema first."
        )

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(schema_sql)

        print("Housing schema created successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
