{{ config(
    materialized = 'incremental',
    unique_key = 'date'
) }}

SELECT
    date,
    avg_max_temp,
    avg_min_temp,
    avg_precipitation_prob,
    max_uv_index,
    weather_conditions,
    LAG(avg_max_temp) OVER (ORDER BY date) AS prev_avg_max_temp,
    LAG(avg_min_temp) OVER (ORDER BY date) AS prev_avg_min_temp,
    LAG(avg_precipitation_prob) OVER (ORDER BY date) AS prev_avg_precipitation_prob,
    LAG(max_uv_index) OVER (ORDER BY date) AS prev_max_uv_index,
    avg_max_temp - LAG(avg_max_temp) OVER (ORDER BY date) AS delta_max_temp,
    avg_min_temp - LAG(avg_min_temp) OVER (ORDER BY date) AS delta_min_temp,
    avg_precipitation_prob - LAG(avg_precipitation_prob) OVER (ORDER BY date) AS delta_precipitation_prob,
    max_uv_index - LAG(max_uv_index) OVER (ORDER BY date) AS delta_uv_index
FROM {{ ref('weather_daily_summary') }}
{% if is_incremental() %}
  WHERE date > (SELECT max(date) FROM {{ this }})
{% endif %}
ORDER BY date
