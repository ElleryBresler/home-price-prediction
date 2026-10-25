
-- --------------------------------------
-- File: model_results.sql
-- Purpose: Store final model metrics and predictions
-- --------------------------------------

-- Store evaluation metrics for each model.
CREATE TABLE IF NOT EXISTS model_evaluation_metrics (
    evaluation_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    model_name TEXT NOT NULL,
    evaluation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dataset_name TEXT NOT NULL,
    mae NUMERIC(12,2) NOT NULL,
    rmse NUMERIC(12,2) NOT NULL,
    r_squared NUMERIC(8,5) NOT NULL
);

-- Store actual and predicted prices for each test sale.
CREATE TABLE IF NOT EXISTS home_price_predictions (
    prediction_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES fact_home_sale(sale_id),
    actual_sale_price NUMERIC(12,2) NOT NULL,
    linear_regression_prediction NUMERIC(12,2) NOT NULL,
    random_forest_prediction NUMERIC(12,2) NOT NULL,
    model_selected TEXT NOT NULL
);
