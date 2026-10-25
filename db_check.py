
# --------------------------------------
# File: db_check.py
# Purpose: Verify PostgreSQL connection and tables
# --------------------------------------

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


def main():
    connection = None

    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST") or os.getenv("PGHOST", "localhost"),
            port=os.getenv("DB_PORT") or os.getenv("PGPORT", "5432"),
            dbname=os.getenv("DB_NAME") or os.getenv(
                "PGDATABASE", "home_price_prediction"
            ),
            user=os.getenv("DB_USER") or os.getenv("PGUSER", "postgres"),
            password=os.getenv("DB_PASSWORD") or os.getenv("PGPASSWORD"),
        )

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    current_database(),
                    current_schema();
            """)
            database, schema = cursor.fetchone()

            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT to_regclass('public.fact_home_sale');
            """)
            home_sale_table = cursor.fetchone()[0]

        print("Database connection successful!")
        print(f"Database: {database}")
        print(f"Current schema: {schema}")
        print("\nTables found in public schema:")

        if tables:
            for table in tables:
                print(f"- {table}")
        else:
            print("No tables found.")

        print("\nCore table check:")
        if home_sale_table:
            print("[PASS] public.fact_home_sale exists.")
        else:
            print("[FAIL] public.fact_home_sale does not exist.")

    except psycopg2.Error as error:
        print("Database check failed.")
        print(error)
        raise

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
