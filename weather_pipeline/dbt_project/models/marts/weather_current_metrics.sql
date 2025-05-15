{{ config(
    materialized = 'incremental',
    unique_key = ['date_time', 'extracted_at']
) }}

SELECT 
    date_time,
    temperature,
    humidity,
    wind_speed,
    sky_condition,
    extracted_at
FROM {{ ref('stg_weather_current') }}

{% if is_incremental() %}
  WHERE extracted_at > (SELECT MAX(extracted_at) FROM {{ this }})
{% endif %}
