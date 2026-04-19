{%- macro cross_join_unnest(arr, col_alias) -%}
    {%- if target.type == 'bigquery' -%}
    UNNEST({{ arr }}) AS {{ col_alias }}
    {%- else -%}
    UNNEST({{ arr }}) AS _unnest_t({{ col_alias }})
    {%- endif -%}
{%- endmacro -%}
