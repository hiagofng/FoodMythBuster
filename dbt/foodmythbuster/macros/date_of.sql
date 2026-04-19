{% macro date_of(ts) %}
    {{ return(adapter.dispatch('date_of')(ts)) }}
{% endmacro %}

{% macro default__date_of(ts) %}
    DATE({{ ts }})
{% endmacro %}

{% macro bigquery__date_of(ts) %}
    DATE({{ ts }})
{% endmacro %}

{% macro duckdb__date_of(ts) %}
    CAST({{ ts }} AS DATE)
{% endmacro %}
