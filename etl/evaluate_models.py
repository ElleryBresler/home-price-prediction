
# --------------------------------------
# File: evaluate_models.py
# Purpose: Evaluate models and save results to PostgreSQL
# --------------------------------------

import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "clean"

load_dotenv(PROJECT_DIR / ".env")


def calculate_metrics(model, X, y):
    """Calculate regression evaluation metrics."""
    predictions = model.predict(X)

    return {
        "MAE": mean_absolute_error(y, predictions),
        "RMSE": mean_squared_error(y, predictions) ** 0.5,
        "R_squared": r2_score(y, predictions),
    }, predictions


def main():
    # Load training data.
    X_train = pd.read_csv(DATA_DIR / "X_train.csv")
    y_train = pd.read_csv(DATA_DIR / "y_train.csv")["sale_price"]

    # Load the untouched final test data from 2010.
    X_test = pd.read_csv(DATA_DIR / "X_test.csv")
    y_test = pd.read_csv(DATA_DIR / "y_test.csv")["sale_price"]

    # Recover sale IDs using the exact sorting and split
    # logic from prepare_model_data.py.
    features = pd.read_csv(DATA_DIR / "ml_features.csv")

    features = features.sort_values(
        ["sale_year", "sale_month", "sale_id"]
    ).reset_index(drop=True)

    test_rows = features[features["sale_year"] == 2010].copy()

    test_sale_ids = test_rows["sale_id"].reset_index(drop=True)
    test_actual_prices = test_rows["sale_price"].reset_index(drop=True)
    y_test = y_test.reset_index(drop=True)

    # Confirm that IDs and test data align before saving anything.
    if len(test_sale_ids) != len(X_test) or len(y_test) != len(X_test):
        raise ValueError(
            "The 2010 sale IDs and test dataset have different row counts. "
            "Check prepare_model_data.py."
        )

    if not test_actual_prices.equals(y_test):
        raise ValueError(
            "The 2010 sale prices do not align with y_test.csv. "
            "Check the row order in prepare_model_data.py."
        )

    # Define both models using the settings already evaluated.
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        ),
    }

    results = []
    prediction_output = pd.DataFrame({
        "sale_id": test_sale_ids,
        "actual_sale_price": y_test,
    })

    print("FINAL MODEL EVALUATION (TEST SET: 2010)")
    print("=" * 55)
    print(f"Test records: {len(X_test)}")

    for name, model in models.items():
        # Fit each model using training data only.
        model.fit(X_train, y_train)

        # Evaluate on the final test set.
        metrics, predictions = calculate_metrics(
            model, X_test, y_test
        )

        results.append({
            "model": name,
            **metrics,
        })

        prediction_column = (
            "linear_regression_prediction"
            if name == "Linear Regression"
            else "random_forest_prediction"
        )
        prediction_output[prediction_column] = predictions

        print(f"\n{name}")
        print("-" * 40)
        print(f"MAE:       ${metrics['MAE']:,.2f}")
        print(f"RMSE:      ${metrics['RMSE']:,.2f}")
        print(f"R-squared: {metrics['R_squared']:.4f}")

    # Random Forest was the better model on the previous test evaluation.
    selected_model = "Random Forest"

    # Save the final metrics and predictions to CSV.
    results_df = pd.DataFrame(results)
    results_df.to_csv(
        DATA_DIR / "final_model_metrics.csv",
        index=False,
    )

    prediction_output.to_csv(
        DATA_DIR / "final_test_predictions.csv",
        index=False,
    )

    # Connect using the same PostgreSQL settings as etl/load.py.
    connection = None

    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "home_price_prediction"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
        )

        with connection:
            with connection.cursor() as cursor:

                # Save both models' evaluation metrics.
                for result in results:
                    cursor.execute(
                        """
                        INSERT INTO model_evaluation_metrics
                            (model_name, dataset_name, mae, rmse, r_squared)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            result["model"],
                            "test_2010",
                            result["MAE"],
                            result["RMSE"],
                            result["R_squared"],
                        ),
                    )

                # Replace the previous prediction output so reruns
                # do not duplicate the 2010 test predictions.
                cursor.execute("DELETE FROM home_price_predictions")

                prediction_rows = [
                    (
                        int(row.sale_id),
                        float(row.actual_sale_price),
                        float(row.linear_regression_prediction),
                        float(row.random_forest_prediction),
                        selected_model,
                    )
                    for row in prediction_output.itertuples(index=False)
                ]

                cursor.executemany(
                    """
                    INSERT INTO home_price_predictions
                        (
                            sale_id,
                            actual_sale_price,
                            linear_regression_prediction,
                            random_forest_prediction,
                            model_selected
                        )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    prediction_rows,
                )

        print("\nSaved evaluation metrics to PostgreSQL.")
        print(
            f"Saved {len(prediction_rows)} test predictions to PostgreSQL."
        )

    except Exception as error:
        print(f"\nDatabase save failed: {error}")
        raise

    finally:
        if connection is not None:
            connection.close()

    print("\nSaved final_model_metrics.csv")
    print("Saved final_test_predictions.csv")
    print(f"Selected model: {selected_model}")
    print("\nFinal evaluation completed.")


if __name__ == "__main__":
    main()
