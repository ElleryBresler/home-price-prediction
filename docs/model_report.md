# Home Price Prediction Model Report

## 1. Project Overview

This project uses the Ames Housing dataset to predict residential home sale prices. The target variable is `sale_price`. The modeling workflow uses a chronological split so that earlier sales are used for training and later sales are reserved for validation and testing.

The current database feature table contains 1,460 records:

| Dataset | Years | Records |
|---|---|---:|
| Training | 2006–2008 | 947 |
| Validation | 2009 | 338 |
| Testing | 2010 | 175 |
| **Total** | **2006–2010** | **1,460** |

The exploratory visualizations in this report were generated using the training dataset only.

## 2. Exploratory Data Analysis

### 2.1 Distribution of Home Sale Prices

![Distribution of Home Sale Prices](figures/sale_price_distribution.png)

The distribution of home sale prices is positively skewed (right-skewed). Most homes in the training data sold for approximately $100,000 to $200,000, while a smaller number sold for substantially higher prices. The long right tail includes a few observations above $500,000.

This pattern indicates that sale prices are not symmetrically distributed and that a relatively small number of expensive properties may contribute to larger prediction errors.

### 2.2 Home Sale Price vs. Overall Quality

![Home Sale Price vs. Overall Quality](figures/price_vs_quality.png)

The scatter plot shows a positive association between overall quality and sale price. Homes with higher overall quality ratings generally sold for more than homes with lower ratings. However, there is considerable variation in sale prices within each quality rating. This suggests that overall quality is informative, but does not explain sale price on its own.

### 2.3 Home Sale Price vs. Above-Ground Living Area

![Home Sale Price vs. Above-Ground Living Area](figures/price_vs_living_area.png)

The scatter plot shows a positive association between above-ground living area and sale price. In general, homes with more living area sold for higher prices. The relationship is not perfectly linear, and sale prices vary substantially among homes with similar living areas. A few unusually large or expensive properties are also visible.

This suggests that living area is likely to be a useful predictor, while other property characteristics also contribute to sale price.

## 3. Baseline and Model Evaluation

Mean Absolute Error (MAE) was selected as the primary evaluation metric. MAE represents the average absolute difference between predicted and actual sale prices, in dollars. Lower values indicate better predictive performance.

The baseline model used the average sale price from the training dataset ($182,104.54) to predict every home in the validation dataset. The resulting validation MAE was $59,407.42. This means the baseline predictions were off by approximately $59,407 per home on average.

Three predictive models were trained using the training dataset and evaluated using the validation dataset. The baseline and candidate model results are shown below.

| Model | Validation MAE |
|---|---:|
| Training-mean baseline | $59,407.42 |
| Linear Regression | $22,774.28 |
| Random Forest | $23,052.44 |
| **Gradient Boosting Regressor** | **$20,683.22** |

Gradient Boosting achieved the lowest validation MAE of $20,683.22 and was selected as the final model. Its validation error was approximately 65.2% lower than the baseline error.

Although Random Forest and Linear Regression both substantially outperformed the baseline, Gradient Boosting provided the strongest validation performance.

## 4. Final Test Evaluation

Gradient Boosting was selected using validation performance and then evaluated on the held-out test dataset. The test dataset contained 175 home sales from 2010 and was not used to select the model.

- **Selected model:** Gradient Boosting Regressor
- **Validation MAE:** $20,683.22
- **Test MAE:** $22,079.09

The test MAE was approximately 6.7% higher than the validation MAE. This indicates reasonably consistent predictive performance on the unseen test dataset. On average, the model's predicted home prices differed from actual sale prices by approximately $22,079.

## 5. Model Interpretation

The Gradient Boosting model identified overall quality as its most important feature, accounting for 54.86% of total feature importance. Above-ground living area was the second most important feature at 21.04%, followed by garage capacity at 7.62%. Neighborhood (Noridge) and house age at sale contributed 3.86% and 2.70%, respectively.

These results suggest that property quality and size are particularly important inputs for predicting home sale prices. Feature importance represents the model's reliance on each variable and should not be interpreted as evidence of causation.

## 6. Limitations and Considerations

The exploratory plots show associations between individual features and sale price; they do not establish causation. The plots also show variation and some unusually high-priced observations, so predictions may be less accurate for properties that differ substantially from the majority of the training data.

The project includes Census socioeconomic information dated 2023 alongside home sales from 2006–2010. Because that information post-dates the sales, its use may introduce temporal information leakage if the intended use is to simulate predictions that could have been made at the time of each historical sale. This limitation should be considered when interpreting model performance and describing the intended prediction scenario.

The model was evaluated using historical Ames Housing data. Its performance may not generalize to other geographic markets or housing conditions without additional validation.

## 7. Conclusion

The project developed and evaluated three predictive models for residential home sale prices using the Ames Housing dataset. Exploratory analysis showed that sale prices are right-skewed and positively associated with overall quality and above-ground living area.

Of the three predictive models, Gradient Boosting achieved the lowest validation MAE at $20,683.22 and was selected for final evaluation. It achieved a test MAE of $22,079.09, indicating reasonably consistent performance on the held-out test dataset.

The feature importance results showed that overall quality and above-ground living area were the two most influential predictors in the selected model. These findings suggest that property characteristics provide useful information for estimating residential sale prices.

The model's performance should be interpreted in light of the historical dataset and the use of 2023 Census information alongside earlier home sales. Future improvements could include using socioeconomic data from years closer to each sale and evaluating the model on additional housing markets.
