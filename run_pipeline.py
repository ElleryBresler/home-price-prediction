
# --------------------------------------
# File: run_pipeline.py
# Purpose: Run the complete home-price prediction pipeline
# --------------------------------------

import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


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
