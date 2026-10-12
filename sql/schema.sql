
-- Remove existing tables so this schema can be rerun.
DROP TABLE IF EXISTS fact_home_sale CASCADE;
DROP TABLE IF EXISTS fact_economic_conditions CASCADE;
DROP TABLE IF EXISTS dim_property CASCADE;
DROP TABLE IF EXISTS dim_location CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

-- One row per housing record in the Ames dataset.
CREATE TABLE dim_property (
    property_id INTEGER PRIMARY KEY,
    overall_qual INTEGER,
    gr_liv_area INTEGER,
    bedroom_abvgr INTEGER,
    full_bath INTEGER,
    year_built INTEGER,
    garage_cars NUMERIC(4,1)
);

-- One row per geographic area represented in the project.
CREATE TABLE dim_location (
    location_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    neighborhood TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL DEFAULT 'Ames',
    county TEXT NOT NULL DEFAULT 'Story',
    state TEXT NOT NULL DEFAULT 'Iowa',
    median_household_income NUMERIC(12,2),
    population INTEGER,
    education_level TEXT
);

-- One row per year and month represented in the project.
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    sale_year INTEGER NOT NULL,
    sale_month INTEGER NOT NULL CHECK (sale_month BETWEEN 1 AND 12),
    sale_quarter INTEGER NOT NULL
        CHECK (sale_quarter BETWEEN 1 AND 4),
    UNIQUE (sale_year, sale_month)
);

-- One row per month of economic observations.
CREATE TABLE fact_economic_conditions (
    economic_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    mortgage_rate NUMERIC(6,3),
    inflation_rate NUMERIC(6,3),
    unemployment_rate NUMERIC(6,3),
    UNIQUE (date_id)
);

-- One row per home sale in the Ames training dataset.
CREATE TABLE fact_home_sale (
    sale_id INTEGER PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES dim_property(property_id),
    location_id INTEGER NOT NULL REFERENCES dim_location(location_id),
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    sale_price NUMERIC(12,2) NOT NULL CHECK (sale_price > 0)
);
