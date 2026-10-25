# Missing Data Report

## Overview

The transformation pipeline combines the Ames Housing Dataset with Census demographic data and Federal Reserve Economic Data (FRED) mortgage-rate observations. Missing values are checked after transformation and in the machine-learning feature dataset to ensure the selected fields are ready for modeling.

## Missing Data Summary

The most recent successful pipeline run reported the following:

| Table or dataset | Missing data result | Explanation |
|---|---|---|
| `dim_property` | 0 missing values in selected fields | Selected property features were populated. |
| `dim_location` | 0 missing values in selected fields | Neighborhood and selected Census fields were populated. |
| `dim_date` | 0 missing values in selected fields | Date keys and date attributes were populated. |
| `fact_home_sale` | 0 missing values in sale and key fields | Sale prices and required relationships were populated. |
| `fact_economic_conditions` | 0 missing mortgage rates | Mortgage-rate observations were populated for the generated monthly records. |
| Machine-learning feature dataset | No missing values found | The feature check found no missing values in the 1,460-row modeling dataset, including the new `house_age_at_sale` feature. |

These results describe the latest successful pipeline run. They do not establish that the original source files never contained missing values.

## Missing Data Treatment and Decisions

- **Property features:** The pipeline uses selected property fields for modeling. The latest feature check found no missing values in the selected modeling dataset.
- **Census demographics:** The project uses selected Census API measures for Ames, Iowa. The latest transformed location data contained no missing values in the selected Census fields.
- **Mortgage rates:** FRED observations are aligned to the project's monthly date keys. The latest quality checks found no missing mortgage rates in the generated economic records.
- **Derived features:** The pipeline calculates `sale_quarter` from the sale month and `house_age_at_sale` by subtracting `year_built` from `sale_year`. The latest feature check reported no missing values in the resulting modeling dataset.
- **Unused economic indicators:** Inflation and unemployment are outside the current project scope. They were not retained as empty fields in the project schema.
- **Unknown values:** Missing values are not automatically replaced with zero, because zero can represent a meaningful numeric value rather than an unknown value.

The available pipeline results confirm that the selected fields were complete after transformation. The current report does not quantify missing values in every original source column before transformation; those counts should not be inferred from the final results.

## Validation

The latest pipeline run passed all eight automated data quality checks, including row counts, key uniqueness, valid sale prices, foreign-key relationships, and mortgage-rate completeness.

The machine-learning feature check also reported no missing values and zero duplicate sale IDs across 1,460 records. The updated modeling dataset includes 39 predictors, and the chronological split contains 947 training records, 338 validation records, and 175 test records.

## Conclusion

The selected modeling fields were complete in the latest successful run. The addition of `house_age_at_sale` did not introduce missing values into the modeling dataset. Future changes to source data or selected features should be accompanied by updated missing-data checks and documentation of any new treatment decisions.