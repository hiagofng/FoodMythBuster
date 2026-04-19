{%- set is_bq = target.type == 'bigquery' -%}
{{
  config(
    materialized='table',
    cluster_by=['category_tag'] if is_bq else none
  )
}}

-- One row per OFF category tag. Pre-aggregates the ratio of "deceptive"
-- products (health claim + NOVA 4) vs. all products carrying a health
-- claim in that category. Directly powers the dashboard's Tile 3
-- ("healthy junk by category") with a single-row-per-category scan
-- instead of re-aggregating stg_products on every dashboard load.

WITH exploded AS (
    SELECT
        product_id,
        category_tag,
        is_deceptive,
        has_health_claim
    FROM {{ ref('stg_products') }},
         {{ cross_join_unnest('categories_tags', 'category_tag') }}
    WHERE has_health_claim
)

SELECT
    category_tag,
    COUNT(*)                                      AS products_with_claim,
    {{ countif('is_deceptive') }}                 AS deceptive_products,
    {{ safe_divide(countif('is_deceptive'), 'COUNT(*)') }}  AS deceptive_share
FROM exploded
GROUP BY category_tag
HAVING products_with_claim >= 5
