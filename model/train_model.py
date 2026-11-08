
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
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error



# PROJECT CONFIGURATION

PROJECT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_DIR / ".env")


def connect_db():
    """Connect to the PostgreSQL database."""

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "home_price_prediction"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
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

    finally:
        connection.close()



# RUN SCRIPT

if __name__ == "__main__":
    main()
