
# --------------------------------------
# File: run_pipeline.py
# Purpose: Run the complete home-price prediction pipeline
# --------------------------------------

import subprocess
import sys
from pathlib import Path
import os
import psycopg2
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent
def check_database_schema():
    """Verify that the core PostgreSQL tables exist before running the pipeline."""
    load_dotenv(PROJECT_DIR / ".env")

    connection = None
    required_tables = {
        "dim_property",
        "dim_location",
        "dim_date",
        "fact_economic_conditions",
        "fact_home_sale",
    }

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
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE';
            """)
            existing_tables = {row[0] for row in cursor.fetchall()}

        missing_tables = required_tables - existing_tables

        if missing_tables:
            raise RuntimeError(
                "Required database tables are missing: "
                f"{sorted(missing_tables)}. "
                "Initialize the database by executing sql/schema.sql "
                "against the database configured in .env, then rerun."
            )

        print("Database schema check passed.", flush=True)

    finally:
        if connection is not None:
            connection.close()

def run_step(description, script_path):
    """Run one pipeline script and stop if it fails."""
    full_path = PROJECT_DIR / script_path

    print(f"\n{'=' * 60}", flush=True)
    print(f"STARTING: {description}", flush=True)
    print(f"{'=' * 60}", flush=True)

    if not full_path.exists():
        raise FileNotFoundError(
            f"Pipeline script not found: {full_path}"
        )

    subprocess.run(
        [sys.executable, str(full_path)],
        cwd=PROJECT_DIR,
        check=True,
    )

    print(f"COMPLETED: {description}", flush=True)


def main():
    steps = [
        # 1. Extract source data.
        ("Extract Census data", "etl/extract_census.py"),
        ("Extract FRED mortgage data", "etl/extract_fred.py"),

        # 2. Transform, load, and validate database data.
        ("Transform source data", "etl/transform.py"),
        ("Load PostgreSQL tables", "etl/load.py"),
        ("Run data quality checks", "etl/quality_checks.py"),

        # 3. Create the machine-learning feature dataset.
        ("Build ML features", "etl/build_features.py"),
        ("Check ML features", "etl/check_features.py"),

        # 4. Prepare chronological training and test datasets.
        ("Prepare model data", "etl/prepare_model_data.py"),

        # 5. Train and compare models.
        ("Train baseline model", "etl/train_baseline.py"),
        ("Train Random Forest model", "etl/train_random_forest.py"),

        # 6. Ensure result tables exist, evaluate final models,
        # and save metrics and predictions to PostgreSQL.
        ("Create model results tables", "etl/create_result_tables.py"),
        ("Evaluate models and save results", "etl/evaluate_models.py"),
    ]

    print("HOME PRICE PREDICTION PIPELINE", flush=True)
    try:
        check_database_schema()
    except Exception as error:
        print(f"\nPIPELINE FAILED: {error}", flush=True)
        sys.exit(1)
    try:
        for description, script_path in steps:
            run_step(description, script_path)

    except subprocess.CalledProcessError as error:
        print(
            f"\nPIPELINE FAILED: {error.cmd}",
            flush=True,
        )
        print(
            f"Exit code: {error.returncode}",
            flush=True,
        )
        sys.exit(error.returncode)

    except Exception as error:
        print(f"\nPIPELINE FAILED: {error}", flush=True)
        sys.exit(1)

    print("\n" + "=" * 60, flush=True)
    print("PIPELINE COMPLETED SUCCESSFULLY!", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
