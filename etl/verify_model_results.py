
# --------------------------------------
# File: verify_model_results.py
# Purpose: Run SQL to verify saved model results
# --------------------------------------

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")


def main():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "home_price_prediction"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )

    try:
        sql_file = PROJECT_DIR / "sql" / "verify_model_results.sql"
        sql_text = sql_file.read_text(encoding="utf-8")

        with connection.cursor() as cursor:
            # Run each SELECT statement separately.
            statements = [
                statement.strip()
                for statement in sql_text.split(";")
                if statement.strip()
            ]

            for statement in statements:
                cursor.execute(statement)

                print("\nQUERY RESULTS")
                print("-" * 50)

                columns = [column[0] for column in cursor.description]
                print(" | ".join(columns))

                for row in cursor.fetchall():
                    print(" | ".join(str(value) for value in row))

    finally:
        connection.close()


if __name__ == "__main__":
    main()
