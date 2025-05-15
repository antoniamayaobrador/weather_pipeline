{{ config(
    materialized = 'incremental',
    unique_key = 'date'
) }}

WITH latest_current AS (
    SELECT
        date_time::date AS date,
        temperature AS current_temperature,
        humidity AS current_humidity,
        wind_speed AS current_wind_speed,
        sky_condition AS current_sky_condition,
        extracted_at,
        ROW_NUMBER() OVER (PARTITION BY date_time::date ORDER BY extracted_at DESC) AS rn
    FROM {{ ref('weather_current_metrics') }}
)

SELECT
    d.*, 
    l.current_temperature,
    l.current_humidity,
    l.current_wind_speed,
    l.current_sky_condition,
    l.extracted_at AS current_extracted_at
FROM {{ ref('weather_daily_summary') }} d
LEFT JOIN latest_current l ON d.date = l.date AND l.rn = 1
{% if is_incremental() %}
  WHERE d.date > (SELECT max(date) FROM {{ this }})
{% endif %}
ORDER BY d.date
