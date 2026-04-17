-- Tile 4: Top Brands selling deceptive products
-- Looker Studio Custom Query data source
-- Replace YOUR_PROJECT with your GCP project ID

SELECT
  ANY_VALUE(brands) AS brand,
  COUNT(*) AS products
FROM `YOUR_PROJECT.foodmythbuster.stg_products`
WHERE is_deceptive
  AND brands IS NOT NULL
  AND brands != ''
GROUP BY LOWER(
  REGEXP_REPLACE(NORMALIZE(TRIM(brands), NFD), r'\p{Mn}', '')
)
ORDER BY products DESC
LIMIT 10
