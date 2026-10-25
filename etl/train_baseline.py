
# --------------------------------------
# File: train_baseline.py
# Purpose: Train a baseline home-price prediction model
# --------------------------------------

from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "clean"


def evaluate_model(model, X, y, dataset_name):
    """Evaluate model predictions using common regression metrics."""
    predictions = model.predict(X)

    mae = mean_absolute_error(y, predictions)
    rmse = mean_squared_error(y, predictions) ** 0.5
    r2 = r2_score(y, predictions)

    print(f"\n{dataset_name} RESULTS")
    print("-" * 40)
    print(f"MAE:  ${mae:,.2f}")
    print(f"RMSE: ${rmse:,.2f}")
    print(f"R-squared: {r2:.4f}")

    return predictions


def main():
    # Load the prepared training and validation data.
    X_train = pd.read_csv(DATA_DIR / "X_train.csv")
    y_train = pd.read_csv(DATA_DIR / "y_train.csv")["sale_price"]

    X_validation = pd.read_csv(DATA_DIR / "X_validation.csv")
    y_validation = pd.read_csv(
        DATA_DIR / "y_validation.csv"
    )["sale_price"]

    # Create and train the baseline linear regression model.
    model = LinearRegression()
    model.fit(X_train, y_train)

    print("BASELINE MODEL: LINEAR REGRESSION")
    print("=" * 50)
    print(f"Training records: {len(X_train)}")
    print(f"Predictor columns: {X_train.shape[1]}")

    # Evaluate on the training data.
    evaluate_model(model, X_train, y_train, "TRAINING")

    # Evaluate on validation data to assess performance on a later year.
    validation_predictions = evaluate_model(
        model,
        X_validation,
        y_validation,
        "VALIDATION (2009)",
    )

    # Save validation predictions for review.
    validation_results = pd.DataFrame({
        "actual_sale_price": y_validation,
        "predicted_sale_price": validation_predictions,
    })

    validation_results.to_csv(
        DATA_DIR / "baseline_validation_predictions.csv",
        index=False,
    )

    print("\nValidation predictions saved.")
    print("Baseline model training completed.")


if __name__ == "__main__":
    main()