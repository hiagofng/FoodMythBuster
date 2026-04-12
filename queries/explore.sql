-- FoodMythBuster — exploratory queries
-- Run: duckdb data/foodmythbuster.duckdb < queries/explore.sql

-- 1. Product count by NOVA group
SELECT
    nova_group,
    count(*)                                                AS products,
    round(count(*) * 100.0 / sum(count(*)) OVER (), 1)     AS pct
FROM staging.stg_products
GROUP BY nova_group
ORDER BY nova_group;

-- 2. Health-claim products: how many are ultra-processed?
SELECT
    nova_group,
    count(*)                                                AS with_claim,
    round(avg(is_ultra_processed::INT) * 100, 1)            AS pct_nova4
FROM staging.stg_products
WHERE has_health_claim
GROUP BY nova_group
ORDER BY nova_group;

-- 3. The paradox: Nutri-Score A but still NOVA 4
SELECT product_id, product_name, brands,
       nutriscore_grade, nova_group, additives_count, matched_health_claims
FROM staging.stg_products
WHERE is_nutriscore_a_but_nova4
ORDER BY additives_count DESC
LIMIT 20;

-- 4. Most deceptive brands (min 5 products)
SELECT
    brands,
    count(*)                                                AS total,
    sum(is_deceptive::INT)                                  AS deceptive,
    round(avg(is_deceptive::INT) * 100, 1)                  AS deceptive_pct
FROM staging.stg_products
WHERE brands IS NOT NULL
GROUP BY brands
HAVING count(*) >= 5
ORDER BY deceptive_pct DESC
LIMIT 20;

-- 5. Most common health claims on NOVA 4 products
SELECT
    UNNEST(matched_health_claims)                           AS claim,
    count(*)                                                AS occurrences
FROM staging.stg_products
WHERE is_ultra_processed AND has_health_claim
GROUP BY claim
ORDER BY occurrences DESC;
