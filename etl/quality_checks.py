
# --------------------------------------
# File: quality_checks.py
# Purpose: Validate the loaded PostgreSQL data
# --------------------------------------

import os
import sys

import psycopg2
from dotenv import load_dotenv


PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
load_dotenv(os.path.join(PROJECT_DIR, ".env"))


def main():
    connection = None
    failures = 0

    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "home_price_prediction"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
        )

        with connection.cursor() as cursor:

            def check(label, sql, condition, description):
                nonlocal failures

                cursor.execute(sql)
                result = cursor.fetchone()[0]
                passed = condition(result)

                status = "PASS" if passed else "FAIL"
                print(f"[{status}] {label}: {description(result)}")

                if not passed:
                    failures += 1

            print("\nDATA QUALITY CHECKS")
            print("=" * 50)

            # 1. Expected property row count
            check(
                "Property row count",
                "SELECT COUNT(*) FROM dim_property;",
                lambda n: n == 1460,
                lambda n: f"{n} rows; expected 1460",
            )

            # 2. Expected neighborhood row count
            check(
                "Location row count",
                "SELECT COUNT(*) FROM dim_location;",
                lambda n: n == 25,
                lambda n: f"{n} rows; expected 25",
            )

            # 3. Expected date row count
            check(
                "Date row count",
                "SELECT COUNT(*) FROM dim_date;",
                lambda n: n == 55,
                lambda n: f"{n} rows; expected 55",
            )

            # 4. Every home sale has a valid positive sale price
            check(
                "Sale prices",
                """
                SELECT COUNT(*)
                FROM fact_home_sale
                WHERE sale_price IS NULL OR sale_price <= 0;
                """,
                lambda n: n == 0,
                lambda n: f"{n} invalid or missing sale prices; expected 0",
            )

            # 5. Property IDs are unique
            check(
                "Property key uniqueness",
                """
                SELECT COUNT(*) - COUNT(DISTINCT property_id)
                FROM dim_property;
                """,
                lambda n: n == 0,
                lambda n: f"{n} duplicate property IDs; expected 0",
            )

            # 6. Location IDs and neighborhood names are unique
            check(
                "Location key uniqueness",
                """
                SELECT
                    (COUNT(*) - COUNT(DISTINCT location_id))
                    +
                    (COUNT(*) - COUNT(DISTINCT neighborhood))
                FROM dim_location;
                """,
                lambda n: n == 0,
                lambda n: f"{n} duplicate key/name instances; expected 0",
            )

            # 7. No home sale references a missing dimension row
            check(
                "Foreign key relationships",
                """
                SELECT COUNT(*)
                FROM fact_home_sale AS s
                LEFT JOIN dim_property AS p
                    ON s.property_id = p.property_id
                LEFT JOIN dim_location AS l
                    ON s.location_id = l.location_id
                LEFT JOIN dim_date AS d
                    ON s.date_id = d.date_id
                WHERE p.property_id IS NULL
                   OR l.location_id IS NULL
                   OR d.date_id IS NULL;
                """,
                lambda n: n == 0,
                lambda n: f"{n} orphaned sales; expected 0",
            )

            # 8. Every date has a mortgage rate.
            check(
                "Mortgage rate completeness",
                """
                SELECT COUNT(*)
                FROM fact_economic_conditions
                WHERE mortgage_rate IS NULL;
                """,
                lambda n: n == 0,
                lambda n: f"{n} missing mortgage rates; expected 0",
            )


        print("\n" + "=" * 50)
        print(f"Checks passed: {8 - failures}/8")
        print(f"Checks failed: {failures}")

        if failures:
            print("Quality checks failed.")
            sys.exit(1)

        print("All automated quality checks passed.")

    except Exception as error:
        print(f"\nQuality check error: {error}")
        raise

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()
