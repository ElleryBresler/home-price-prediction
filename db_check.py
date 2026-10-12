import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def main():
    connection = None

    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "home_price_prediction"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
        )

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)

            tables = cursor.fetchall()

        print("Database connection successful!")
        print("Tables found:")

        for (table_name,) in tables:
            print(f"- {table_name}")

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
