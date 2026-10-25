-- One row per housing record in the Ames dataset.
CREATE TABLE IF NOT EXISTS dim_property (
    property_id INTEGER PRIMARY KEY,
    overall_qual INTEGER,
    gr_liv_area INTEGER,
    bedroom_abvgr INTEGER,
    full_bath INTEGER,
    year_built INTEGER,
    garage_cars NUMERIC(4,1)
);

-- One row per geographic area represented in the project.
CREATE TABLE IF NOT EXISTS dim_location (
    location_id INTEGER PRIMARY KEY,
    neighborhood TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL DEFAULT 'Ames',
    county TEXT NOT NULL DEFAULT 'Story',
    state TEXT NOT NULL DEFAULT 'Iowa',
    median_household_income NUMERIC(12,2),
    population INTEGER,
    bachelors_degree_count INTEGER
);

-- One row per year and month represented in the project.
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    sale_year INTEGER NOT NULL,
    sale_month INTEGER NOT NULL CHECK (sale_month BETWEEN 1 AND 12),
    sale_quarter INTEGER NOT NULL CHECK (sale_quarter BETWEEN 1 AND 4),
    UNIQUE (sale_year, sale_month)
);

-- One row per month of economic observations.
CREATE TABLE IF NOT EXISTS fact_economic_conditions (
    economic_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    mortgage_rate NUMERIC(6,3),
    UNIQUE (date_id)
);

-- One row per home sale in the Ames dataset.
CREATE TABLE IF NOT EXISTS fact_home_sale (
    sale_id INTEGER PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES dim_property(property_id),
    location_id INTEGER NOT NULL REFERENCES dim_location(location_id),
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    sale_price NUMERIC(12,2) NOT NULL CHECK (sale_price > 0)
);

-- Stores evaluation metrics for each model and dataset.
CREATE TABLE IF NOT EXISTS model_evaluation_metrics (
    evaluation_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    model_name TEXT NOT NULL,
    evaluation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dataset_name TEXT NOT NULL,
    mae NUMERIC(14,2) NOT NULL,
    rmse NUMERIC(14,2) NOT NULL,
    r_squared NUMERIC(8,5) NOT NULL
);

-- Stores model predictions for each tested home sale.
CREATE TABLE IF NOT EXISTS home_price_predictions (
    prediction_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sale_id INTEGER NOT NULL REFERENCES fact_home_sale(sale_id),
    actual_sale_price NUMERIC(12,2) NOT NULL,
    linear_regression_prediction NUMERIC(12,2) NOT NULL,
    random_forest_prediction NUMERIC(12,2) NOT NULL,
    model_selected TEXT NOT NULL
);
