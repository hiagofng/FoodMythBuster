{% macro parse_json_array(col) %}
    {{ return(adapter.dispatch('parse_json_array')(col)) }}
{% endmacro %}

{% macro default__parse_json_array(col) %}
    JSON_EXTRACT_STRING_ARRAY({{ col }})
{% endmacro %}

{% macro bigquery__parse_json_array(col) %}
    JSON_EXTRACT_STRING_ARRAY({{ col }})
{% endmacro %}

{% macro duckdb__parse_json_array(col) %}
    {{ col }}::JSON::VARCHAR[]
{% endmacro %}
