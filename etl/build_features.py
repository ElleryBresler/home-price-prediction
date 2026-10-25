
# --------------------------------------
# File: build_features.py
# Purpose: Build and load the machine-learning feature table
# --------------------------------------

import os
import re
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_DIR / ".env")


def connect_db():
    """Connect using the project's existing DB_ or PG_ environment variables."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST") or os.getenv("PGHOST", "localhost"),
        port=os.getenv("DB_PORT") or os.getenv("PGPORT", "5432"),
        dbname=os.getenv("DB_NAME") or os.getenv("PGDATABASE", "home_price_prediction"),
        user=os.getenv("DB_USER") or os.getenv("PGUSER", "postgres"),
        password=os.getenv("DB_PASSWORD") or os.getenv("PGPASSWORD"),
    )


def main():
    connection = connect_db()

    try:
        query = """
            SELECT
                s.sale_id,
                p.overall_qual,
                p.gr_liv_area,
                p.bedroom_abvgr,
                p.full_bath,
                p.year_built,
                p.garage_cars,
                l.neighborhood,
                l.median_household_income,
                l.population,
                l.bachelors_degree_count,
                d.sale_year,
                d.sale_month,
                d.sale_quarter,
                e.mortgage_rate,
                s.sale_price
            FROM fact_home_sale AS s
            JOIN dim_property AS p
                ON s.property_id = p.property_id
            JOIN dim_location AS l
                ON s.location_id = l.location_id
            JOIN dim_date AS d
                ON s.date_id = d.date_id
            LEFT JOIN fact_economic_conditions AS e
                ON s.date_id = e.date_id
            ORDER BY s.sale_id;
        """

        features = pd.read_sql_query(query, connection)

        # Calculate the home's age at the time of sale.
        features["house_age_at_sale"] = (
            features["sale_year"] - features["year_built"]
        )

        # Preserve the original CSV used by the existing modeling scripts.
        output_path = PROJECT_DIR / "data" / "clean" / "ml_features.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        features.to_csv(output_path, index=False)

        # Assign the same time-based splits used by the modeling workflow.
        features["split"] = "train"
        features.loc[features["sale_year"] == 2009, "split"] = "validate"
        features.loc[features["sale_year"] == 2010, "split"] = "test"

        # One-hot encode neighborhood so the database table contains
        # model-ready categorical features.
        encoded = pd.get_dummies(
            features,
            columns=["neighborhood"],
            prefix="neighborhood",
            dtype=int,
        )

        # Create safe, consistent SQL column names for neighborhood fields.
        rename_columns = {}
        for column in encoded.columns:
            if column.startswith("neighborhood_"):
                suffix = column[len("neighborhood_"):]
                suffix = re.sub(r"[^a-zA-Z0-9_]", "_", suffix.lower())
                rename_columns[column] = f"neighborhood_{suffix}"

        encoded = encoded.rename(columns=rename_columns)

        # PostgreSQL table columns and types.
        column_types = {
            "sale_id": "INTEGER PRIMARY KEY",
            "overall_qual": "INTEGER",
            "gr_liv_area": "INTEGER",
            "bedroom_abvgr": "INTEGER",
            "full_bath": "INTEGER",
            "year_built": "INTEGER",
            "house_age_at_sale": "INTEGER",
            "garage_cars": "NUMERIC(4,1)",
            "median_household_income": "NUMERIC(12,2)",
            "population": "INTEGER",
            "bachelors_degree_count": "INTEGER",
            "sale_year": "INTEGER",
            "sale_month": "INTEGER",
            "sale_quarter": "INTEGER",
            "mortgage_rate": "NUMERIC(6,3)",
            "sale_price": "NUMERIC(12,2) NOT NULL",
            "split": "TEXT NOT NULL CHECK (split IN ('train', 'validate', 'test'))",
        }

        for column in encoded.columns:
            if column.startswith("neighborhood_"):
                column_types[column] = "INTEGER NOT NULL DEFAULT 0"

        columns = list(encoded.columns)


        # Refresh only the ML feature table's data.
        # Its structure is defined in sql/schema.sql.
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ml_feature_table;")

            columns = list(encoded.columns)

            insert_query = sql.SQL(
                "INSERT INTO ml_feature_table ({}) VALUES %s"
            ).format(
                sql.SQL(", ").join(
                    sql.Identifier(column) for column in columns
                )
            )

            rows = [
                tuple(None if pd.isna(value) else value for value in row)
                for row in encoded.itertuples(index=False, name=None)
            ]

            execute_values(
                cursor,
                insert_query.as_string(connection),
                rows,
            )

        connection.commit()


        print(f"Original modeling CSV saved: {output_path}")
        print(f"Original feature rows: {len(features)}")
        print(f"PostgreSQL ML feature rows: {len(encoded)}")
        print(f"Encoded feature columns: {len(encoded.columns)}")
        print("\nRows by split:")
        print(encoded["split"].value_counts().sort_index())

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
