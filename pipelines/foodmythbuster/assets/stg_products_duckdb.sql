/* @bruin
name: staging.stg_products
type: duckdb.sql
connection: duckdb_default
materialization:
  type: table
  strategy: create+replace
depends:
  - raw.off_brazil_products
@bruin */

WITH base AS (
    SELECT
        code                                                AS product_id,
        product_name,
        nova_group,
        CASE WHEN LOWER(nutriscore_grade) IN ('a','b','c','d','e')
             THEN LOWER(nutriscore_grade)
        END                                                   AS nutriscore_grade,
        CASE LOWER(nutriscore_grade)
            WHEN 'a' THEN 1 WHEN 'b' THEN 2 WHEN 'c' THEN 3
            WHEN 'd' THEN 4 WHEN 'e' THEN 5
        END                                                 AS nutriscore_numeric,
        brands,
        categories,
        labels_tags::JSON::VARCHAR[]                        AS labels_tags,
        categories_tags::JSON::VARCHAR[]                    AS categories_tags,
        additives_tags::JSON::VARCHAR[]                     AS additives_tags,
        additives_n,
        len(additives_tags::JSON::VARCHAR[])                AS additives_count,
        ingredients_text,
        ingredients_n,
        epoch_ms(created_t * 1000)                          AS created_at,
        CAST(epoch_ms(created_t * 1000) AS DATE)            AS created_date,
        EXTRACT(YEAR FROM epoch_ms(created_t * 1000))       AS created_year,
        list_intersect(
            labels_tags::JSON::VARCHAR[],
            ['en:organic', 'en:bio', 'en:natural', 'en:light',
             'en:fit', 'en:no-sugar', 'en:zero-sugar', 'en:low-fat',
             'en:low-calories', 'en:high-protein', 'en:vegan',
             'en:vegetarian', 'en:gluten-free', 'en:no-preservatives']
        )                                                   AS matched_health_claims,
        nova_group = 4                                      AS is_ultra_processed,
        LOWER(nutriscore_grade) = 'a' AND nova_group = 4              AS is_nutriscore_a_but_nova4
    FROM raw.off_brazil_products
    WHERE nova_group   IS NOT NULL
      AND product_name IS NOT NULL
)

SELECT
    *,
    len(matched_health_claims) > 0                                  AS has_health_claim,
    len(matched_health_claims) > 0 AND is_ultra_processed           AS is_deceptive
FROM base
