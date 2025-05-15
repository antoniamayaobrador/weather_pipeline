{{ config(
    materialized = 'incremental',
    unique_key = 'date'
) }}

WITH extremes AS (
    SELECT
        date,
        avg_max_temp,
        avg_min_temp,
        avg_precipitation_prob,
        max_uv_index,
        weather_conditions,
        ROW_NUMBER() OVER (ORDER BY avg_max_temp DESC) AS hottest_day,
        ROW_NUMBER() OVER (ORDER BY avg_min_temp ASC) AS coldest_day,
        ROW_NUMBER() OVER (ORDER BY avg_precipitation_prob DESC) AS wettest_day,
        ROW_NUMBER() OVER (ORDER BY max_uv_index DESC) AS highest_uv_day
    FROM {{ ref('weather_daily_summary') }}
)

SELECT * FROM extremes
WHERE (hottest_day = 1 OR coldest_day = 1 OR wettest_day = 1 OR highest_uv_day = 1)
{% if is_incremental() %}
  AND date > (SELECT max(date) FROM {{ this }})
{% endif %}
ORDER BY date
