# Residential Home Sale Price Prediction

## Business Question

What is the expected residential home sale price based on property characteristics, location, and economic conditions?

## Target Variable

Sale price (`SalePrice`).

## Prediction Unit

One row in my ML feature table = one residential home sale.

## Data Sources

| Source | What it provides | Access |
|---|---|---|
| Ames Housing Dataset | Property characteristics and historical sale prices | Downloadable dataset |
| U.S. Census Bureau API | Population, household income, and demographic information | API |
| Federal Reserve Economic Data (FRED) API | Economic indicators, such as mortgage rates | API |

## How to Run

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with required API credentials and database settings.
4. Run the extraction scripts in `etl/`.
5. Run `sql/schema.sql` against PostgreSQL.
6. Run `python db_check.py` to verify the database tables.

## AI Usage

ChatGPT was used to help interpret assignment requirements, plan the database structure, and develop and document code. Code and data-source choices will be reviewed and tested by the student.