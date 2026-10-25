
# --------------------------------------
# File: train_random_forest.py
# Purpose: Train a Random Forest home-price model
# --------------------------------------

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "clean"


def evaluate_model(model, X, y, dataset_name):
    """Evaluate model predictions using regression metrics."""
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
    # Load the same training and validation datasets used
    # for the baseline linear regression model.
    X_train = pd.read_csv(DATA_DIR / "X_train.csv")
    y_train = pd.read_csv(DATA_DIR / "y_train.csv")["sale_price"]

    X_validation = pd.read_csv(DATA_DIR / "X_validation.csv")
    y_validation = pd.read_csv(
        DATA_DIR / "y_validation.csv"
    )["sale_price"]

    # Create the Random Forest model.
    model = RandomForestRegressor(
        n_estimators=300,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    # Train the model.
    model.fit(X_train, y_train)

    print("RANDOM FOREST REGRESSION MODEL")
    print("=" * 50)
    print(f"Training records: {len(X_train)}")
    print(f"Predictor columns: {X_train.shape[1]}")
    print("Number of trees: 300")

    # Evaluate on training data.
    evaluate_model(model, X_train, y_train, "TRAINING")

    # Evaluate on the 2009 validation data.
    validation_predictions = evaluate_model(
        model,
        X_validation,
        y_validation,
        "VALIDATION (2009)",
    )

    # Save validation predictions for comparison.
    validation_results = pd.DataFrame({
        "actual_sale_price": y_validation,
        "predicted_sale_price": validation_predictions,
    })

    validation_results.to_csv(
        DATA_DIR / "random_forest_validation_predictions.csv",
        index=False,
    )

    # Save feature importance for interpretation.
    importance = pd.DataFrame({
        "feature": X_train.columns,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)

    importance.to_csv(
        DATA_DIR / "random_forest_feature_importance.csv",
        index=False,
    )

    print("\nValidation predictions saved.")
    print("Feature importance saved.")
    print("Random Forest training completed.")


if __name__ == "__main__":
    main()
