# Residential Home Sale Price Prediction

## Business Question

What is the expected residential home sale price based on property characteristics, location, and economic conditions?

## Target Variable

Sale price (`SalePrice` in the original Ames Housing dataset; stored as `sale_price` in the project database and modeling files).

## Prediction Unit

One row in the machine-learning feature table represents one residential home sale.

## Project Overview

This project combines residential property characteristics, demographic and socioeconomic information, and historical mortgage rates to predict home sale prices in Ames, Iowa.

The project includes data extraction, transformation, PostgreSQL storage, automated data quality checks, feature engineering, model training, and evaluation. Two regression models are compared: Linear Regression as the baseline and Random Forest as the improved model.

## Data Sources

This project uses three data sources:

1. **Ames Housing Dataset (Kaggle):** Provides residential property characteristics and historical sale prices.
2. **U.S. Census Bureau API:** Provides demographic and socioeconomic data for Ames, Iowa.
3. **Federal Reserve Economic Data (FRED) API:** Provides historical 30-year fixed mortgage rates.

### 1. Ames Housing Dataset

The Ames Housing dataset was obtained from the [House Prices: Advanced Regression Techniques competition on Kaggle](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques/data).

To obtain the dataset:

1. Sign in to Kaggle and download the competition data.
2. Extract the downloaded files.
3. Place `train.csv` in the `data/manual/` directory.

Expected file path:

```text
data/manual/train.csv
```

The dataset contains 1,460 residential property records and 81 columns. The original `SalePrice` field is the target variable.

The downloaded dataset is excluded from version control through `.gitignore`. Anyone cloning this repository must obtain the dataset separately before running the pipeline.

To validate the downloaded file, run:

```powershell
python etl/check_ames_data.py
```

### 2. U.S. Census Bureau API

The Census Bureau API provides demographic and socioeconomic information for Ames, Iowa, using selected American Community Survey five-year estimates.

Extraction script:

```text
etl/extract_census.py
```

Run independently with:

```powershell
python etl/extract_census.py
```

The raw API response is saved to:

```text
data/raw/census_ames_raw.json
```

### 3. Federal Reserve Economic Data (FRED) API

The FRED API provides historical 30-year fixed mortgage rates using the `MORTGAGE30US` series.

Extraction script:

```text
etl/extract_fred.py
```

A valid FRED API key must be stored in a local `.env` file using the variable name `FRED_API_KEY`.

Run independently with:

```powershell
python etl/extract_fred.py
```

The raw API response is saved to:

```text
data/raw/fred_mortgage_raw.json
```

Mortgage rates are incorporated into the project as an economic feature. Inflation and unemployment are not included in the current model.

## Database Design

PostgreSQL stores the analytical data using a star-schema design.

The core database tables are defined in `sql/schema.sql`:

- `dim_date`
- `dim_location`
- `dim_property`
- `fact_economic_conditions`
- `fact_home_sale`

The machine-learning feature dataset joins property, location, sale date, sale price, and mortgage-rate information into one row per home sale.

Model results are stored in two additional tables defined in `sql/model_results.sql`:

- `model_evaluation_metrics`: Stores model evaluation metrics, including MAE, RMSE, and R².
- `home_price_predictions`: Stores actual sale prices, predictions from both models, the sale identifier, and the selected model.

## ETL Pipeline

The Python pipeline performs the following steps:

1. Extract Census API data.
2. Extract FRED mortgage-rate data.
3. Transform and clean the source data.
4. Load the core tables into PostgreSQL.
5. Run automated data quality checks.
6. Build the machine-learning feature dataset.
7. Check the feature dataset.
8. Prepare chronological training, validation, and test datasets.
9. Train the baseline and Random Forest models.
10. Create the model-results tables if they do not exist.
11. Evaluate both models on the final test set and save metrics and predictions to PostgreSQL.

The feature dataset contains 1,460 home sales and 16 columns before categorical encoding.

The chronological split is:

| Dataset | Sale years | Records |
|---|---|---:|
| Training | 2006–2008 | 947 |
| Validation | 2009 | 338 |
| Final test | 2010 | 175 |

The final test set is kept separate from model training and is used to compare final model performance.

## Data Quality

The pipeline includes eight automated data quality checks covering:

- Expected row counts for core tables.
- Missing or invalid sale prices.
- Duplicate property identifiers.
- Duplicate location keys or names.
- Orphaned foreign-key relationships.
- Missing mortgage rates.

The checks run through:

```powershell
python etl/quality_checks.py
```

The feature dataset is also checked for missing values and duplicate sale identifiers using:

```powershell
python etl/check_features.py
```

## Modeling Approach

### Baseline: Linear Regression

Linear Regression provides a baseline for predicting home sale prices using the prepared property, neighborhood, demographic, and economic features.

### Improved Model: Random Forest

Random Forest is compared with Linear Regression to evaluate whether a nonlinear model improves prediction performance.

The Random Forest model uses 300 trees, a minimum leaf size of two, and a fixed random seed of 42.

### Final Test Results

The following results were obtained on the 2010 test set of 175 home sales.

| Metric | Linear Regression | Random Forest |
|---|---:|---:|
| Mean Absolute Error (MAE) | $24,218.70 | $22,559.80 |
| Root Mean Squared Error (RMSE) | $37,350.86 | $34,755.61 |
| R² | 0.7832 | 0.8123 |

Random Forest performed better on all three test metrics and was selected as the final model.

Its MAE of approximately $22,560 indicates the average absolute difference between predicted and actual sale prices in the test set. Its R² of 0.8123 indicates that it explains approximately 81.2% of the variation in test-set sale prices relative to a mean-price benchmark.

These results represent one chronological test period and should not be interpreted as a guarantee of performance in other years or housing markets.

### Model Outputs

The final evaluation generates the following files in `data/clean/`:

- `final_model_metrics.csv`
- `final_test_predictions.csv`

The metrics and predictions are also written to PostgreSQL for downstream analysis and reporting.

## How to Run

### Prerequisites

- Python installed.
- PostgreSQL installed and running.
- Access to the Kaggle Ames Housing dataset.
- A FRED API key.
- A local `.env` file containing the database settings and API credentials.

### Initial Setup

1. Clone the repository.
2. Download the Kaggle dataset and place `train.csv` in `data/manual/`.
3. Create and activate a Python virtual environment.
4. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

5. Create a local `.env` file with the database settings expected by the scripts:

   ```text
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=home_price_prediction
   DB_USER=postgres
   DB_PASSWORD=your_local_password
   FRED_API_KEY=your_fred_api_key
   ```

   Replace the example values with your actual local configuration. Do not commit `.env` to GitHub.

6. Create the core database tables by executing `sql/schema.sql` against your PostgreSQL database.

### Run the Pipeline

From the project root, with the virtual environment activated, run:

```powershell
python run_pipeline.py
```

The pipeline runs extraction, transformation, database loading, data quality checks, feature preparation, model training, and final evaluation in sequence. It stops if a pipeline step fails.

The core database schema must exist before the first run. The model-results tables are created automatically by the pipeline if they do not already exist.

### Verify Model Results

To verify that evaluation metrics and predictions were saved to PostgreSQL, run:

```powershell
python etl/verify_model_results.py
```

The verification script reports the most recent model evaluation records and the number of saved predictions and unique home sales.

## Data Documentation

Additional documentation is maintained in:

- `docs/field_sources.md`: Documents field sources and origins.
- `docs/missing_data.md`: Documents missing-data handling decisions.

See `docs/data_flow.png` if the data-flow diagram is included in the repository.

## Version Control and Reproducibility

The project uses Git and GitHub for version control. Python dependencies are recorded in `requirements.txt`, and a virtual environment is used to isolate project dependencies.

The `.gitignore` file excludes environment variables, the virtual environment, downloaded raw data, and generated clean data files.

## AI Usage

ChatGPT was used to help interpret assignment requirements, plan the database structure, troubleshoot code, and develop documentation. The student reviewed and tested the project code and evaluated the model outputs.
