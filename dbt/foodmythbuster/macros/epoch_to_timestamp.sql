{% macro epoch_to_timestamp(col) %}
    {{ return(adapter.dispatch('epoch_to_timestamp')(col)) }}
{% endmacro %}

{% macro default__epoch_to_timestamp(col) %}
    TIMESTAMP_SECONDS({{ col }})
{% endmacro %}

{% macro bigquery__epoch_to_timestamp(col) %}
    TIMESTAMP_SECONDS({{ col }})
{% endmacro %}

{% macro duckdb__epoch_to_timestamp(col) %}
    to_timestamp({{ col }})
{% endmacro %}
