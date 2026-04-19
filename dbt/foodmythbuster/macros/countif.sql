{% macro countif(cond) %}
    {{ return(adapter.dispatch('countif')(cond)) }}
{% endmacro %}

{% macro default__countif(cond) %}
    COUNTIF({{ cond }})
{% endmacro %}

{% macro bigquery__countif(cond) %}
    COUNTIF({{ cond }})
{% endmacro %}

{% macro duckdb__countif(cond) %}
    COUNT(*) FILTER (WHERE {{ cond }})
{% endmacro %}
