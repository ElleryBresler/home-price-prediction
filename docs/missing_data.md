# Missing Data Report

## Overview

The transformation pipeline processes the Ames housing dataset and external Census and FRED data to create five clean tables. Missing values were checked after transformation.

## Missing Data Summary

| Table | Column | Missing Values | Explanation |
|---|---|---:|---|
| `dim_property` | Selected property fields | 0 | All selected property fields are populated. |
| `dim_location` | Location and Census fields | 0 | Neighborhood and Census-related fields are populated. |
| `dim_date` | Date fields | 0 | All date fields are populated. |
| `fact_home_sale` | Sale and key fields | 0 | All sale and key fields are populated. |
| `fact_economic_conditions` | `mortgage_rate` | 0 | Mortgage rates were populated for the generated monthly records. |

## Missing Data Treatment

The project uses the selected property, location, date, sale, and mortgage-rate fields. Inflation and unemployment were removed from the schema because their data sources had not been integrated into the pipeline. Rather than retaining empty columns, the project focuses on the mortgage rate as its selected economic indicator.

Missing values are not replaced with zero because zero would represent an actual value rather than an unknown value.

## Conclusion

The selected fields were populated in the most recent successful pipeline run. The automated quality checks verify expected row counts, key uniqueness, valid sale prices, foreign key relationships, and mortgage-rate completeness.
