## How to Run

Follow these steps to set up the project on a new computer and run the complete home price prediction pipeline.

### Prerequisites

Before starting, make sure you have:

- Python installed.
- PostgreSQL installed and running.
- Access to the [Ames Housing dataset on Kaggle](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques/data).
- A FRED API key.
- Git installed.

### Step 1: Clone the Repository

```powershell
git clone https://github.com/ElleryBresler/home-price-prediction.git
cd home-price-prediction
```

### Step 2: Obtain the Ames Housing Dataset

Download the House Prices: Advanced Regression Techniques competition data from Kaggle. Extract the downloaded files and place `train.csv` in:

```text
data/manual/train.csv
```

The dataset is excluded from version control and must be obtained separately.

Validate the downloaded file:

```powershell
python etl/check_ames_data.py
```

The validation script checks that the file exists and contains the columns required by the project.

### Step 3: Create and Activate a Python Virtual Environment

From the project root, create a virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a local `.env` file by copying the provided template:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder values with your local PostgreSQL credentials and FRED API key.

The configuration includes:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=home_price_prediction
DB_USER=postgres
DB_PASSWORD=your_local_password
FRED_API_KEY=your_fred_api_key
```

Use your actual local credentials. Do not commit `.env` to GitHub or share credentials publicly.

### Step 5: Create the PostgreSQL Database

Using pgAdmin or another PostgreSQL administration tool, create an empty database named `home_price_prediction`, matching the `DB_NAME` setting in `.env`.

The database must exist before the schema can be initialized. The initialization script creates the project tables but does not create the PostgreSQL database itself.

### Step 6: Initialize the Database Schema

With the virtual environment activated and `.env` configured, run:

```powershell
python init_housing_schema.py
```

This script executes `sql/schema.sql` to create missing project tables. The schema uses `CREATE TABLE IF NOT EXISTS` statements and does not intentionally drop existing tables.

The pipeline checks that the required core tables exist before beginning data extraction. If tables are missing, it stops and displays an error explaining that the schema must be initialized.

### Step 7: Run the Complete Pipeline

From the project root, run:

```powershell
python run_pipeline.py
```

The pipeline performs these operations in sequence:

1. Extract demographic and socioeconomic data from the U.S. Census Bureau API.
2. Extract historical mortgage rates from the FRED API.
3. Transform the source data and generate dimension and fact table CSV files.
4. Load the transformed data into PostgreSQL.
5. Run eight automated data quality checks.
6. Build and validate the machine-learning feature dataset.
7. Prepare chronological training, validation, and test datasets.
8. Train the baseline Linear Regression model.
9. Train the Random Forest model.
10. Create the model-results tables if they do not exist.
11. Evaluate both models on the final test set and save metrics and predictions to PostgreSQL.

The pipeline stops if a step fails. Review the error message before continuing.

### Step 8: Verify the Results

After a successful run, verify the saved model results:

```powershell
python etl/verify_model_results.py
```

The pipeline generates these files in `data/clean/`:

- `final_model_metrics.csv`
- `final_test_predictions.csv`

These files are excluded from version control and are recreated when the pipeline runs.

### Reproducibility Notes

Python dependencies are specified in `requirements.txt`, and `.env.example` documents the required environment variables. The `.gitignore` file excludes secrets, the virtual environment, downloaded source data, and generated data files.

A new user must obtain the Kaggle dataset, configure PostgreSQL and the FRED API key, create the database, and initialize the schema before running the pipeline. After these prerequisites are complete, `python run_pipeline.py` executes the complete workflow.
