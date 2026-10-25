SELECT *
FROM model_evaluation_metrics
ORDER BY evaluation_id DESC;

SELECT
    COUNT(*) AS prediction_count,
    COUNT(DISTINCT sale_id) AS unique_sales,
    MIN(actual_sale_price) AS minimum_actual_price,
    MAX(actual_sale_price) AS maximum_actual_price
FROM home_price_predictions;