{%- macro except_columns(cols) -%}
    {%- if target.type == 'bigquery' -%}
    EXCEPT({{ cols }})
    {%- else -%}
    EXCLUDE ({{ cols }})
    {%- endif -%}
{%- endmacro -%}
