{% macro match_health_claims(labels_col) %}
    {{ return(adapter.dispatch('match_health_claims')(labels_col)) }}
{% endmacro %}

{% macro default__match_health_claims(labels_col) %}
    ARRAY(
        SELECT c.claim_tag
        FROM {{ ref('health_claims') }} c
        WHERE c.claim_tag IN UNNEST({{ labels_col }})
    )
{% endmacro %}

{% macro bigquery__match_health_claims(labels_col) %}
    ARRAY(
        SELECT c.claim_tag
        FROM {{ ref('health_claims') }} c
        WHERE c.claim_tag IN UNNEST({{ labels_col }})
    )
{% endmacro %}

{% macro duckdb__match_health_claims(labels_col) %}
    list_intersect(
        {{ labels_col }},
        (SELECT list(claim_tag) FROM {{ ref('health_claims') }})
    )
{% endmacro %}
