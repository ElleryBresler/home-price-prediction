
# --------------------------------------
# File: train_model.py
# Author: Ellery Hill (Bresler)
# Purpose: Read ML features and explore training data
# Created: November 7th, 2026
# --------------------------------------
import os
from pathlib import Path

import pandas as pd
import psycopg2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor


# PROJECT CONFIGURATION

PROJECT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_DIR / ".env")


def connect_db():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )


# MAIN FUNCTION

def main():

    connection = connect_db()

    try:

        
        # STEP 1: READ ML FEATURE TABLE

        query = """
            SELECT *
            FROM ml_feature_table
            ORDER BY sale_id;
        """

        df = pd.read_sql_query(query, connection)

        print("ML FEATURE TABLE")

        print(f"Total records: {len(df)}")

        # Separate data using the split column.
        train = df[df["split"] == "train"].copy()
        validate = df[df["split"] == "validate"].copy()
        test = df[df["split"] == "test"].copy()

        # Display dataset counts.
        print("\nDATASET SPLITS")

        print(f"Training records: {len(train)}")
        print(f"Validation records: {len(validate)}")
        print(f"Testing records: {len(test)}")

        # Check that no dataset is empty.
        if train.empty or validate.empty or test.empty:
            raise ValueError("One or more dataset splits are empty.")

       
        # STEP 2: EXPLORE TRAINING DATA
      
        # Create folder for saved visualizations.
        figures_dir = PROJECT_DIR / "docs" / "figures"
        figures_dir.mkdir(parents=True, exist_ok=True)

        # Convert chart columns to numeric values.
        train["sale_price"] = pd.to_numeric(train["sale_price"])
        train["overall_qual"] = pd.to_numeric(train["overall_qual"])
        train["gr_liv_area"] = pd.to_numeric(train["gr_liv_area"])

       
        # CHART 1: SALE PRICE DISTRIBUTION

        plt.figure(figsize=(10, 6))

        plt.hist(
            train["sale_price"],
            bins=30,
            edgecolor="black"
        )

        plt.title("Distribution of Home Sale Prices")
        plt.xlabel("Sale Price ($)")
        plt.ylabel("Number of Homes")

        plt.tight_layout()

        plt.savefig(
            figures_dir / "sale_price_distribution.png",
            dpi=300
        )

        plt.close()

       


        # CHART 2: PRICE VS. OVERALL QUALITY

        plt.figure(figsize=(10, 6))

        plt.scatter(
            train["overall_qual"],
            train["sale_price"],
            alpha=0.5
        )

        plt.title("Home Sale Price vs. Overall Quality")
        plt.xlabel("Overall Quality Rating")
        plt.ylabel("Sale Price ($)")

        plt.tight_layout()

        plt.savefig(
            figures_dir / "price_vs_quality.png",
            dpi=300
        )

        plt.close()


        # CHART 3: PRICE VS. LIVING AREA

        plt.figure(figsize=(10, 6))

        plt.scatter(
            train["gr_liv_area"],
            train["sale_price"],
            alpha=0.5
        )

        plt.title("Home Sale Price vs. Above-Ground Living Area")
        plt.xlabel("Above-Ground Living Area (Square Feet)")
        plt.ylabel("Sale Price ($)")

        plt.tight_layout()

        plt.savefig(
            figures_dir / "price_vs_living_area.png",
            dpi=300
        )

        plt.close()



        
        # STEP 3: BASELINE MODEL

        # Calculate the average sale price using training data.
        baseline_price = train["sale_price"].mean()

        # Predict the same average price for every validation home.
        baseline_predictions = [baseline_price] * len(validate)

        # Calculate Mean Absolute Error.
        baseline_mae = mean_absolute_error(
            validate["sale_price"],
            baseline_predictions
        )

        # Display baseline results.
        print("\nBASELINE MODEL RESULTS")

        print(f"Average training sale price: ${baseline_price:,.2f}")
        print(f"Baseline validation MAE: ${baseline_mae:,.2f}")

        # STEP 5: LINEAR REGRESSION MODEL

        # Separate the predictors (X) from the target (y)
        columns_to_remove = ["sale_id", "split", "sale_price"]

        X_train = train.drop(columns=columns_to_remove)
        y_train = train["sale_price"]

        X_validate = validate.drop(columns=columns_to_remove)
        y_validate = validate["sale_price"]

        # Keep numeric features only
        X_train = X_train.select_dtypes(include="number")
        X_validate = X_validate[X_train.columns]

        # Create and train the Linear Regression model
        linear_model = LinearRegression()
        linear_model.fit(X_train, y_train)

        # Make predictions using the validation data
        linear_predictions = linear_model.predict(X_validate)

        # Calculate validation MAE
        linear_mae = mean_absolute_error(
            y_validate,
            linear_predictions
        )

        print("\nLINEAR REGRESSION RESULTS")
        print(f"Validation MAE: ${linear_mae:,.2f}")

        # STEP 5: RANDOM FOREST MODEL

        random_forest = RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )

        # Train the model
        random_forest.fit(X_train, y_train)

        # Make validation predictions
        rf_predictions = random_forest.predict(X_validate)

        # Calculate validation MAE
        rf_mae = mean_absolute_error(
            y_validate,
            rf_predictions
        )

        print("\nRANDOM FOREST RESULTS")
        print(f"Validation MAE: ${rf_mae:,.2f}")

        # STEP 5: GRADIENT BOOSTING MODEL

        gradient_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )

        # Train the model
        gradient_model.fit(X_train, y_train)

        # Make validation predictions
        gradient_predictions = gradient_model.predict(X_validate)

        # Calculate validation MAE
        gradient_mae = mean_absolute_error(
            y_validate,
            gradient_predictions
        )

        print("\nGRADIENT BOOSTING RESULTS")
        print(f"Validation MAE: ${gradient_mae:,.2f}")

                # MODEL COMPARISON

        model_comparison = pd.DataFrame({
            "Model": [
                "Baseline",
                "Linear Regression",
                "Random Forest",
                "Gradient Boosting"
            ],
            "Validation MAE": [
                baseline_mae,
                linear_mae,
                rf_mae,
                gradient_mae
            ]
        })

        model_comparison = model_comparison.sort_values(
            "Validation MAE"
        )

        print("\nMODEL COMPARISON")
        print(model_comparison.to_string(
            index=False,
            formatters={
                "Validation MAE": "${:,.2f}".format
            }
        ))

        best_model_name = model_comparison.iloc[0]["Model"]

        print(f"\nSelected model: {best_model_name}")

        
        # STEP 6: FINAL TEST EVALUATION

        # Use the selected Gradient Boosting model on test data
        X_test = test.drop(columns=columns_to_remove)
        y_test = test["sale_price"]

        X_test = X_test[X_train.columns]

        test_predictions = gradient_model.predict(X_test)

        test_mae = mean_absolute_error(
            y_test,
            test_predictions
        )

        print("\nFINAL TEST RESULTS")
        print(f"Selected model: {best_model_name}")
        print(f"Validation MAE: ${gradient_mae:,.2f}")
        print(f"Test MAE: ${test_mae:,.2f}")

        # STEP 7: FEATURE IMPORTANCE

        feature_importance = pd.DataFrame({
            "Feature": X_train.columns,
            "Importance": gradient_model.feature_importances_
        })

        # Sort features from most important to least important
        feature_importance = feature_importance.sort_values(
            by="Importance",
            ascending=False
        )

        # Display the top five features
        print("\nTOP 5 MOST IMPORTANT FEATURES")
        print(feature_importance.head(5).to_string(
            index=False,
            formatters={
                "Importance": "{:.4f}".format
            }
        ))

                # STEP 8: SAVE PREDICTIONS TO POSTGRESQL

        # Generate predictions for all three data splits
        train_predictions = gradient_model.predict(X_train)
        validate_predictions = gradient_model.predict(X_validate)

        # Combine actual and predicted values
        predictions_df = pd.concat([
            pd.DataFrame({
                "sale_id": train["sale_id"],
                "split": "train",
                "actual": y_train,
                "predicted": train_predictions
            }),
            pd.DataFrame({
                "sale_id": validate["sale_id"],
                "split": "validate",
                "actual": y_validate,
                "predicted": validate_predictions
            }),
            pd.DataFrame({
                "sale_id": test["sale_id"],
                "split": "test",
                "actual": y_test,
                "predicted": test_predictions
            })
        ], ignore_index=True)

        # Calculate prediction error
        predictions_df["error"] = (
            predictions_df["actual"] - predictions_df["predicted"]
        )

        predictions_df["model_name"] = best_model_name

        # Clear previous predictions
        cursor = connection.cursor()
        cursor.execute("DELETE FROM home_price_predictions")

        # Insert updated predictions
        insert_query = """
            INSERT INTO home_price_predictions
            (sale_id, split, actual, predicted, error, model_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        records = predictions_df[
            ["sale_id", "split", "actual", "predicted", "error", "model_name"]
        ].values.tolist()

        cursor.executemany(insert_query, records)

        connection.commit()
        cursor.close()

        print(f"\nSaved {len(predictions_df)} predictions to PostgreSQL.")

        
    finally:
        connection.close()



# RUN SCRIPT

if __name__ == "__main__":
    main()
