{{ config(
    materialized = 'incremental',
    unique_key = 'date'
) }}

SELECT
    TO_DATE(forecast_date) AS date,
    MAX(extracted_at) AS last_updated,
    AVG(max_temp) AS avg_max_temp,
    AVG(min_temp) AS avg_min_temp,
    MAX(max_temp) AS highest_temp,
    MIN(min_temp) AS lowest_temp,
    AVG(precipitation_probability) AS avg_precipitation_prob,
    MAX(precipitation_probability) AS max_precipitation_prob,
    MAX(uv_index) AS max_uv_index,
    LISTAGG(DISTINCT sky_condition, ', ') AS weather_conditions
FROM {{ ref('stg_weather_forecast_daily') }}
{% if is_incremental() %}
  WHERE TO_DATE(forecast_date) > (SELECT max(date) FROM {{ this }})
{% endif %}
GROUP BY date
ORDER BY date
