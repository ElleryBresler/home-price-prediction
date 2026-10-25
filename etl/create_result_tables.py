
# --------------------------------------
# File: create_result_tables.py
# Purpose: Create tables for model metrics and predictions
# --------------------------------------

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# Find the project root and load database settings.
PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")


def main():
    connection = None

    try:
        # Use the same PostgreSQL connection settings as load.py.
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "home_price_prediction"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
        )

        # Read the SQL file containing the table definitions.
        sql_file = PROJECT_DIR / "sql" / "model_results.sql"
        sql_text = sql_file.read_text(encoding="utf-8")

        # Execute each CREATE TABLE statement.
        with connection:
            with connection.cursor() as cursor:
                for statement in sql_text.split(";"):
                    if statement.strip():
                        cursor.execute(statement)

        print("Model results tables created successfully.")

    except Exception as error:
        print(f"Could not create model results tables: {error}")
        raise

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
