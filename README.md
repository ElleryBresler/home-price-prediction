# Residential Home Sale Price Prediction

## Business Question

What is the expected residential home sale price based on property characteristics, location, and economic conditions?

## Target Variable

Sale price (`SalePrice`).

## Prediction Unit

One row in my ML feature table = one residential home sale.

## Data Sources

This project combines three data sources to support residential home sale price analysis and prediction.

1. **Ames Housing Dataset (Kaggle):** Provides residential property characteristics and historical sale prices. The target variable is `SalePrice`.
2. **U.S. Census Bureau API:** Provides demographic and socioeconomic data for Ames, Iowa.
3. **Federal Reserve Economic Data (FRED) API:** Provides historical 30-year fixed mortgage rates.

### 1. Ames Housing Dataset

The Ames Housing dataset was obtained from the [House Prices: Advanced Regression Techniques competition on Kaggle](https://www.kaggle.com/competitions/house-prices-advanced-regression-techniques/data).

To obtain the dataset:

1. Sign in to Kaggle and download the competition data.
2. Extract the downloaded files.
3. Place `train.csv` in the `data/manual/` directory.

The expected file path is:

```text
data/manual/train.csv
```

The dataset contains 1,460 residential property records and 81 columns. The `SalePrice` field is the target variable for the planned home price prediction model.

The downloaded dataset is excluded from version control through `.gitignore`. Anyone cloning this repository must obtain the dataset separately before running the Ames data validation script.

To validate the downloaded file, run:

```powershell
python etl/check_ames_data.py
```

### 2. U.S. Census Bureau API

The Census Bureau API provides demographic and socioeconomic information for Ames, Iowa. The extraction script retrieves selected American Community Survey five-year estimates.

The script is located at:

```text
etl/extract_census.py
```

Run the script with:

```powershell
python etl/extract_census.py
```

The raw API response is saved to:

```text
data/raw/census_ames_raw.json
```

### 3. Federal Reserve Economic Data (FRED) API

The FRED API provides historical 30-year fixed mortgage rates using the `MORTGAGE30US` series.

The extraction script is located at:

```text
etl/extract_fred.py
```

A valid FRED API key must be stored in a local `.env` file using the variable name `FRED_API_KEY`.

Run the script with:

```powershell
python etl/extract_fred.py
```

The raw API response is saved to:

```text
data/raw/fred_mortgage_raw.json
```

The current extraction script retrieves mortgage rate observations. Additional economic indicators, such as inflation and unemployment, may be incorporated in future development.

### Data Storage and Version Control

The project uses PostgreSQL to organize the planned analytical dataset using a star schema. The schema is defined in `sql/schema.sql` and includes the following tables:

- `dim_date`
- `dim_location`
- `dim_property`
- `fact_economic_conditions`
- `fact_home_sale`

Raw API responses, downloaded competition data, environment variables, and local development files are excluded from version control. API keys must never be committed to the repository.

## How to Run

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with required API credentials and database settings.
4. Run the extraction scripts in `etl/`.
5. Run `sql/schema.sql` against PostgreSQL.
6. Run `python db_check.py` to verify the database tables.

## AI Usage

ChatGPT was used to help interpret assignment requirements, plan the database structure, and develop and document code. Code and data-source choices will be reviewed and tested by the student.