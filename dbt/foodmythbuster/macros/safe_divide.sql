{% macro safe_divide(num, denom) %}
    {{ return(adapter.dispatch('safe_divide')(num, denom)) }}
{% endmacro %}

{% macro default__safe_divide(num, denom) %}
    SAFE_DIVIDE({{ num }}, {{ denom }})
{% endmacro %}

{% macro bigquery__safe_divide(num, denom) %}
    SAFE_DIVIDE({{ num }}, {{ denom }})
{% endmacro %}

{% macro duckdb__safe_divide(num, denom) %}
    ({{ num }}) / NULLIF(({{ denom }}), 0)
{% endmacro %}
