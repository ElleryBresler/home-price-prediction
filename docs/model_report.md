# Home Price Prediction Model Report

## 1. Project Overview

This project uses the Ames Housing dataset to predict residential home
sale prices. The target variable is `sale_price`. The modeling workflow
uses a chronological split so that earlier sales are used for training
and later sales are reserved for validation and testing.

The current database feature table contains 1,460 records:

  Dataset                 Years     Records
  ------------ ---------------- -----------
  Training           2006--2008         947
  Validation               2009         338
  Testing                  2010         175
  **Total**      **2006--2010**   **1,460**

The exploratory visualizations in this report were generated using the
training dataset only.

## 2. Exploratory Data Analysis

### 2.1 Distribution of Home Sale Prices

**Figure:** `figures/sale_price_distribution.png`

The distribution of home sale prices is positively skewed
(right-skewed). Most homes in the training data sold for approximately
\$100,000 to \$200,000, while a smaller number sold for substantially
higher prices. The long right tail includes a few observations above
\$500,000.

This pattern indicates that sale prices are not symmetrically
distributed and that a relatively small number of expensive properties
may contribute to larger prediction errors.

### 2.2 Home Sale Price vs. Overall Quality

**Figure:** `figures/price_vs_quality.png`

The scatter plot shows a positive association between overall quality
and sale price. Homes with higher overall quality ratings generally sold
for more than homes with lower ratings. However, there is considerable
variation in sale prices within each quality rating. This suggests that
overall quality is informative, but does not explain sale price on its
own.

### 2.3 Home Sale Price vs. Above-Ground Living Area

**Figure:** `figures/price_vs_living_area.png`

The scatter plot shows a positive association between above-ground
living area and sale price. In general, homes with more living area sold
for higher prices. The relationship is not perfectly linear, and sale
prices vary substantially among homes with similar living areas. A few
unusually large or expensive properties are also visible.

This suggests that living area is likely to be a useful predictor, while
other property characteristics also contribute to sale price.

## 3. Baseline and Model Evaluation

*To be completed after the baseline and candidate models are trained.*

The baseline will predict the mean sale price calculated from the
training data for every observation in the validation dataset. Mean
Absolute Error (MAE) will be used as the primary evaluation metric. MAE
represents the average absolute difference between predicted and actual
sale prices, in dollars; lower values indicate better predictive
performance.

The candidate models and their validation results will be documented
here:

  Model                           Validation MAE
  ----------------------------- ----------------
  Training-mean baseline                     TBD
  Linear Regression                          TBD
  Random Forest                              TBD
  Gradient Boosting Regressor                TBD

The final model will be selected using validation performance. The test
dataset will be reserved for the final evaluation of the selected model.

## 4. Final Test Evaluation

*To be completed after selecting the model using validation results and
evaluating that selected model on the test dataset.*

-   Selected model: TBD
-   Test MAE: TBD
-   Interpretation of test performance: TBD

## 5. Model Interpretation

*To be completed after examining the selected model's feature importance
or coefficients.*

This section will identify the features that contributed most to the
selected model's predictions and discuss whether their relationships
with sale price are consistent with the exploratory analysis.

## 6. Limitations and Considerations

The exploratory plots show associations between individual features and
sale price; they do not establish causation. The plots also show
variation and some unusually high-priced observations, so predictions
may be less accurate for properties that differ substantially from the
majority of the training data.

The project includes Census socioeconomic information dated 2023
alongside home sales from 2006--2010. Because that information
post-dates the sales, its use may introduce temporal information leakage
if the intended use is to simulate predictions that could have been made
at the time of each historical sale. This limitation should be
considered when interpreting model performance and describing the
intended prediction scenario.

## 7. Conclusion

The training-data exploration indicates that sale price is positively
associated with both overall quality and above-ground living area. Sale
prices are right-skewed, and the scatter plots show substantial
variation that is not explained by either feature individually. The next
stage of the project will compare the baseline, Linear Regression,
Random Forest, and Gradient Boosting Regressor using validation MAE,
select the strongest candidate, and evaluate it on the held-out test
dataset.
