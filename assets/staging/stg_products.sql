/* @bruin
name: staging.stg_products
type: duckdb.sql
connection: duckdb-default
materialization:
  type: table
depends:
  - raw.off_brazil_products
*/

-- Health/marketing claim tags used as proxy for front-of-pack messaging
WITH base AS (
    SELECT
        code                                                AS product_id,
        product_name,
        nova_group,
        LOWER(nutriscore_grade)                             AS nutriscore_grade,
        CASE LOWER(nutriscore_grade)
            WHEN 'a' THEN 1 WHEN 'b' THEN 2 WHEN 'c' THEN 3
            WHEN 'd' THEN 4 WHEN 'e' THEN 5
        END                                                 AS nutriscore_numeric,
        brands,
        labels_tags,
        categories_tags,
        additives_tags,
        len(additives_tags)                                 AS additives_count,
        ingredients_text,

        -- Overlap with known health-claim tags
        list_has_any(
            labels_tags,
            ['en:organic', 'en:bio', 'en:natural', 'en:light',
             'en:fit', 'en:no-sugar', 'en:zero-sugar', 'en:low-fat',
             'en:low-calories', 'en:high-protein', 'en:vegan',
             'en:vegetarian', 'en:gluten-free', 'en:no-preservatives']
        )                                                   AS has_health_claim,

        list_intersect(
            labels_tags,
            ['en:organic', 'en:bio', 'en:natural', 'en:light',
             'en:fit', 'en:no-sugar', 'en:zero-sugar', 'en:low-fat',
             'en:low-calories', 'en:high-protein', 'en:vegan',
             'en:vegetarian', 'en:gluten-free', 'en:no-preservatives']
        )                                                   AS matched_health_claims,

        nova_group = 4                                      AS is_ultra_processed,
        LOWER(nutriscore_grade) = 'a' AND nova_group = 4    AS is_nutriscore_a_but_nova4,
        ingested_at

    FROM raw.off_brazil_products
    WHERE nova_group   IS NOT NULL
      AND product_name IS NOT NULL
)

SELECT
    *,
    -- Core metric: product carries a health claim but is still ultra-processed
    has_health_claim AND is_ultra_processed                 AS is_deceptive
FROM base
