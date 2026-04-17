-- Tile 2: "Green Label" but Ultra-Processed
-- Looker Studio Custom Query data source
-- Replace YOUR_PROJECT with your GCP project ID

SELECT
  REPLACE(claim, 'en:', '') AS label,
  COUNT(*) AS total,
  COUNTIF(is_ultra_processed) AS nova4,
  ROUND(100.0 * COUNTIF(is_ultra_processed) / COUNT(*), 1) AS pct_nova4
FROM `YOUR_PROJECT.foodmythbuster.stg_products`,
  UNNEST(matched_health_claims) AS claim
WHERE ARRAY_LENGTH(matched_health_claims) > 0
GROUP BY claim
ORDER BY pct_nova4 DESC
