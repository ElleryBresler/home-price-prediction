
# Field Sources Data Dictionary

This document identifies the source, derivation, and purpose of every field in `sql/schema.sql`.

## Dimension Tables

| Table | Field | Comes from | How | Used for |
|---|---|---|---|---|
| dim_property | property_id | Ames Housing Dataset | Original `Id` column | Primary key; links property characteristics to a sale |
| dim_property | overall_qual | Ames Housing Dataset | Original `OverallQual` column | Model feature: overall material and finish quality |
| dim_property | gr_liv_area | Ames Housing Dataset | Original `GrLivArea` column | Model feature: above-ground living area |
| dim_property | bedroom_abvgr | Ames Housing Dataset | Original `BedroomAbvGr` column | Model feature: above-ground bedrooms |
| dim_property | full_bath | Ames Housing Dataset | Original `FullBath` column | Model feature: full bathrooms above grade |
| dim_property | year_built | Ames Housing Dataset | Original `YearBuilt` column | Model feature: construction year |
| dim_property | garage_cars | Ames Housing Dataset | Original `GarageCars` column | Model feature: garage capacity |
| dim_location | location_id | Created by PostgreSQL | Automatically generated identity value | Primary key; identifies a location record |
| dim_location | neighborhood | Ames Housing Dataset | Original `Neighborhood` column | Model feature and geographic reporting |
| dim_location | city | Created from project scope | Constant value: Ames | Dashboard context |
| dim_location | county | Created from project scope | Constant value: Story County; verify geographic metadata | Geographic context |
| dim_location | state | Created from project scope | Constant value: Iowa | Geographic context |
| dim_location | median_household_income | U.S. Census Bureau API | Census income measure; geographic match and field definition must be verified | Potential model feature |
| dim_location | population | U.S. Census Bureau API | Census population measure; geographic match must be verified | Potential model feature |
| dim_location | education_level | U.S. Census Bureau API | Education measure; definition and geographic match must be verified | Potential model feature |
| dim_date | date_id | Calculated in Python | Year multiplied by 100 plus month, e.g. 200802 | Primary key; links sales and economic observations to a month |
| dim_date | sale_year | Ames Housing Dataset | Original `YrSold` column | Model feature and time-based reporting |
| dim_date | sale_month | Ames Housing Dataset | Original `MoSold` column | Model feature and time-based reporting |
| dim_date | sale_quarter | Calculated in Python | Ceiling of sale month divided by 3 | Model feature and seasonal reporting |

## Fact Tables

| Table | Field | Comes from | How | Used for |
|---|---|---|---|---|
| fact_economic_conditions | economic_id | Created by PostgreSQL | Automatically generated identity value | Primary key |
| fact_economic_conditions | date_id | Joined to dim_date | Matches the economic observation's month to `dim_date.date_id` | Foreign key; aligns economic data with sales periods |
| fact_economic_conditions | mortgage_rate | FRED API | Mortgage-rate series; exact series and frequency to be selected | Potential model feature |
| fact_economic_conditions | inflation_rate | FRED API | Inflation series; exact series and frequency to be selected | Potential model feature |
| fact_economic_conditions | unemployment_rate | FRED API | Unemployment series; exact series and frequency to be selected | Potential model feature |
| fact_home_sale | sale_id | Ames Housing Dataset | Original `Id` column | Primary key; identifies each sale record |
| fact_home_sale | property_id | Ames Housing Dataset | Original `Id` column, linked to `dim_property.property_id` | Foreign key |
| fact_home_sale | location_id | Ames Housing Dataset / joined | Neighborhood matched to `dim_location` | Foreign key; supports geographic features and reporting |
| fact_home_sale | date_id | Ames Housing Dataset / calculated in Python | `YrSold` and `MoSold` converted to a year-month key | Foreign key; links the sale to its time period |
| fact_home_sale | sale_price | Ames Housing Dataset | Original `SalePrice` column | Target variable for the predictive model |

## Source Fields Used but Not Stored

- Ames Housing Dataset: `Id`, `Neighborhood`, `YrSold`, `MoSold`, `OverallQual`, `GrLivArea`, `BedroomAbvGr`, `FullBath`, `YearBuilt`, `GarageCars`, and `SalePrice` are mapped to fields in the schema.
- Additional Ames fields are retained in the original local `train.csv` but are not currently included in the database schema.
- Census API: geographic identifiers and any source fields used to select the appropriate geographic records must be documented after the Census geography is selected.
- FRED API: observation dates, series identifiers, and source metadata must be documented when the specific series are selected.

## Outstanding Validation

1. Confirm the Census geographic level and establish whether it can be matched reliably to Ames neighborhoods.
2. Select the exact FRED series, observation frequencies, and date alignment rules.
3. Confirm how missing Census or economic observations will be handled during next week's transformation stage.
4. Ensure that the final schema and this dictionary remain synchronized.
