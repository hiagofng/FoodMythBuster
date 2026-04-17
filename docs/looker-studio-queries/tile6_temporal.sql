-- Tile 6: Temporal Gap — deceptive vs non-deceptive NOVA 4 additive count
-- Looker Studio Custom Query data source
-- Replace YOUR_PROJECT with your GCP project ID

SELECT
  EXTRACT(YEAR FROM created_date) AS created_year,
  AVG(IF(has_health_claim, additives_count, NULL)) AS avg_deceptive,
  AVG(IF(NOT has_health_claim, additives_count, NULL)) AS avg_non_deceptive,
  COUNTIF(has_health_claim) AS deceptive_n,
  COUNTIF(NOT has_health_claim) AS non_deceptive_n
FROM `YOUR_PROJECT.foodmythbuster.stg_products`
WHERE is_ultra_processed
  AND created_date BETWEEN DATE '2020-01-01' AND DATE '2024-12-31'
GROUP BY created_year
ORDER BY created_year
