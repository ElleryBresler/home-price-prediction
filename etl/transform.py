
from pathlib import Path
import json

import pandas as pd

# Project folders
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
MANUAL_DIR = DATA_DIR / "manual"
CLEAN_DIR = DATA_DIR / "clean"


def main():
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------
    # 1. Read the Ames housing data
    # -----------------------------------------
    homes = pd.read_csv(MANUAL_DIR / "train.csv")

    # Keep only the fields needed for this schema.
    homes = homes[
        [
            "Id",
            "Neighborhood",
            "YrSold",
            "MoSold",
            "SalePrice",
            "OverallQual",
            "GrLivArea",
            "BedroomAbvGr",
            "FullBath",
            "YearBuilt",
            "GarageCars",
        ]
    ].copy()

    # Convert the sale year and month to numeric values.
    homes["YrSold"] = pd.to_numeric(homes["YrSold"])
    homes["MoSold"] = pd.to_numeric(homes["MoSold"])

    # -----------------------------------------
    # 2. Read the Census API response
    # -----------------------------------------
    with open(RAW_DIR / "census_ames_raw.json", encoding="utf-8") as file:
        census_data = json.load(file)

    census_headers = census_data[0]
    census_values = census_data[1]

    census = dict(zip(census_headers, census_values))

    median_income = int(census["B19013_001E"])
    population = int(census["B01003_001E"])
    bachelors_count = int(census["B15003_022E"])

    # -----------------------------------------
    # 3. Build the property dimension
    # -----------------------------------------
    dim_property = homes[
        [
            "Id",
            "OverallQual",
            "GrLivArea",
            "BedroomAbvGr",
            "FullBath",
            "YearBuilt",
            "GarageCars",
        ]
    ].rename(
        columns={
            "Id": "property_id",
            "OverallQual": "overall_qual",
            "GrLivArea": "gr_liv_area",
            "BedroomAbvGr": "bedroom_abvgr",
            "FullBath": "full_bath",
            "YearBuilt": "year_built",
            "GarageCars": "garage_cars",
        }
    )

    # -----------------------------------------
    # 4. Build the location dimension
    # -----------------------------------------
    neighborhoods = sorted(homes["Neighborhood"].unique())

    dim_location = pd.DataFrame(
        {
            "location_id": range(1, len(neighborhoods) + 1),
            "neighborhood": neighborhoods,
            "city": "Ames",
            "county": "Story",
            "state": "Iowa",
            "median_household_income": median_income,
            "population": population,
            "bachelors_degree_count": bachelors_count,
        }
    )

    # Map every home's neighborhood to its location ID.
    location_lookup = dict(
        zip(dim_location["neighborhood"], dim_location["location_id"])
    )
    homes["location_id"] = homes["Neighborhood"].map(location_lookup)

    # -----------------------------------------
    # 5. Build the date dimension
    # -----------------------------------------
    sale_months = (
        homes[["YrSold", "MoSold"]]
        .drop_duplicates()
        .sort_values(["YrSold", "MoSold"])
        .reset_index(drop=True)
    )

    sale_months["date_id"] = (
        sale_months["YrSold"] * 100 + sale_months["MoSold"]
    )
    sale_months["sale_quarter"] = ((sale_months["MoSold"] - 1) // 3) + 1

    dim_date = sale_months.rename(
        columns={
            "YrSold": "sale_year",
            "MoSold": "sale_month",
        }
    )[
        ["date_id", "sale_year", "sale_month", "sale_quarter"]
    ]

    date_lookup = dict(
        zip(
            zip(sale_months["YrSold"], sale_months["MoSold"]),
            sale_months["date_id"],
        )
    )

    homes["date_id"] = [
        date_lookup[(year, month)]
        for year, month in zip(homes["YrSold"], homes["MoSold"])
    ]

    # -----------------------------------------
    # 6. Read and summarize FRED mortgage rates
    # -----------------------------------------
    with open(RAW_DIR / "fred_mortgage_raw.json", encoding="utf-8") as file:
        fred_data = json.load(file)

    fred = pd.DataFrame(fred_data["observations"])
    fred["date"] = pd.to_datetime(fred["date"])
    fred["value"] = pd.to_numeric(fred["value"], errors="coerce")

    # FRED uses "." for missing observations.
    fred = fred.dropna(subset=["value"])

    # Average the weekly observations within each month.
    fred["sale_year"] = fred["date"].dt.year
    fred["sale_month"] = fred["date"].dt.month

    monthly_rates = (
        fred.groupby(["sale_year", "sale_month"], as_index=False)["value"]
        .mean()
        .rename(columns={"value": "mortgage_rate"})
    )

    monthly_rates["date_id"] = (
        monthly_rates["sale_year"] * 100 + monthly_rates["sale_month"]
    )

    fact_economic_conditions = dim_date[["date_id"]].merge(
        monthly_rates[["date_id", "mortgage_rate"]],
        on="date_id",
        how="left",
        validate="one_to_one",
    )


    # -----------------------------------------
    # 7. Build the home-sale fact table
    # -----------------------------------------
    fact_home_sale = homes[
        ["Id", "location_id", "date_id", "SalePrice"]
    ].rename(
        columns={
            "Id": "sale_id",
            "SalePrice": "sale_price",
        }
    )

    fact_home_sale["property_id"] = fact_home_sale["sale_id"]

    fact_home_sale = fact_home_sale[
        [
            "sale_id",
            "property_id",
            "location_id",
            "date_id",
            "sale_price",
        ]
    ]

    # -----------------------------------------
    # 8. Save cleaned tables as CSV files
    # -----------------------------------------
    tables = {
        "dim_property": dim_property,
        "dim_location": dim_location,
        "dim_date": dim_date,
        "fact_economic_conditions": fact_economic_conditions,
        "fact_home_sale": fact_home_sale,
    }

    for table_name, dataframe in tables.items():
        output_file = CLEAN_DIR / f"{table_name}.csv"
        dataframe.to_csv(output_file, index=False)
        print(f"Saved {table_name}: {len(dataframe)} rows")

    print("\nTransformation completed.")


if __name__ == "__main__":
    main()
