
# --------------------------------------
# File: build_features.py
# Purpose: Build the machine-learning feature table
# --------------------------------------

import os
from pathlib import Path

import pandas as pd
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

        output_path = PROJECT_DIR / "data" / "clean" / "ml_features.csv"
        features.to_csv(output_path, index=False)

        print(f"Feature table saved to: {output_path}")
        print(f"Rows: {len(features)}")
        print(f"Columns: {len(features.columns)}")
        print("\nFeature table preview:")
        print(features.head())

    finally:
        connection.close()


if __name__ == "__main__":
    main()
