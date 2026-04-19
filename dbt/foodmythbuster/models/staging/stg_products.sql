{%- set is_bq = target.type == 'bigquery' -%}
{{
  config(
    materialized='table',
    partition_by={'field': 'created_date', 'data_type': 'date', 'granularity': 'day'} if is_bq else none,
    cluster_by=['is_deceptive', 'nutriscore_grade', 'is_ultra_processed'] if is_bq else none
  )
}}

-- Raw table stores labels_tags / categories_tags / additives_tags as JSON
-- strings (dlt serialises them to avoid nested-table normalisation). We
-- parse them into native ARRAY<STRING> in `parsed` so the rest of the
-- model works with arrays.

WITH parsed AS (
    SELECT
        * {{ except_columns('labels_tags, categories_tags, additives_tags') }},
        {{ parse_json_array('labels_tags') }}     AS labels_tags,
        {{ parse_json_array('categories_tags') }} AS categories_tags,
        {{ parse_json_array('additives_tags') }}  AS additives_tags
    FROM {{ source('foodmythbuster', 'off_brazil_products') }}
),

base AS (
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
        labels_tags,
        categories_tags,
        additives_tags,
        additives_n,
        ARRAY_LENGTH(additives_tags)                        AS additives_count,
        ingredients_text,
        ingredients_n,
        {{ epoch_to_timestamp('created_t') }}                        AS created_at,
        {{ date_of(epoch_to_timestamp('created_t')) }}                  AS created_date,
        EXTRACT(YEAR FROM {{ epoch_to_timestamp('created_t') }})     AS created_year,
        {{ match_health_claims('labels_tags') }}            AS matched_health_claims,
        nova_group = 4                                      AS is_ultra_processed,
        LOWER(nutriscore_grade) = 'a' AND nova_group = 4              AS is_nutriscore_a_but_nova4
    FROM parsed
    WHERE nova_group   IS NOT NULL
      AND product_name IS NOT NULL
)

SELECT
    *,
    ARRAY_LENGTH(matched_health_claims) > 0                                 AS has_health_claim,
    ARRAY_LENGTH(matched_health_claims) > 0 AND is_ultra_processed          AS is_deceptive
FROM base
