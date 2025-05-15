{{ config(
    materialized = 'view'
) }}

WITH hourly_data AS (
    SELECT
        PRONOSTICO:hoy AS hourly_forecast,
        _AIRBYTE_EXTRACTED_AT AS extracted_at
    FROM {{ source('raw', 'PALMA') }}
),

forecast_date AS (
    SELECT
        extracted_at,
        hourly_forecast:"@attributes":fecha::STRING AS forecast_date
    FROM hourly_data
),

temperatures AS (
    SELECT
        h.extracted_at,
        fd.forecast_date,
        f.index AS hour_index,
        f.value::NUMBER(4,1) AS temperature
    FROM hourly_data h
    JOIN forecast_date fd ON h.extracted_at = fd.extracted_at
    , LATERAL FLATTEN(input => h.hourly_forecast:temperatura) f
),

humidity AS (
    SELECT
        h.extracted_at,
        fd.forecast_date,
        f.index AS hour_index,
        f.value::NUMBER(4,1) AS humidity
    FROM hourly_data h
    JOIN forecast_date fd ON h.extracted_at = fd.extracted_at
    , LATERAL FLATTEN(input => h.hourly_forecast:humedad_relativa) f
),

sky_conditions AS (
    SELECT
        h.extracted_at,
        fd.forecast_date,
        f.index AS hour_index,
        f.value::STRING AS sky_condition
    FROM hourly_data h
    JOIN forecast_date fd ON h.extracted_at = fd.extracted_at
    , LATERAL FLATTEN(input => h.hourly_forecast:estado_cielo_descripcion) f
),

wind AS (
    SELECT
        h.extracted_at,
        fd.forecast_date,
        f.value:"@attributes":periodo::NUMBER AS hour_index,
        f.value:direccion::STRING AS wind_direction,
        f.value:velocidad::NUMBER AS wind_speed
    FROM hourly_data h
    JOIN forecast_date fd ON h.extracted_at = fd.extracted_at
    , LATERAL FLATTEN(input => h.hourly_forecast:viento) f
)

SELECT
    t.extracted_at,
    t.forecast_date,
    t.hour_index,
    CASE 
        WHEN t.hour_index = 0 THEN '00:00'
        WHEN t.hour_index = 6 THEN '06:00'
        WHEN t.hour_index = 12 THEN '12:00'
        WHEN t.hour_index = 18 THEN '18:00'
        ELSE t.hour_index || ':00'
    END AS time_of_day,
    COALESCE(t.temperature, 0) AS temperature,
    COALESCE(h.humidity, 0) AS humidity,
    COALESCE(s.sky_condition, 'unknown') AS sky_condition,
    COALESCE(w.wind_direction, 'unknown') AS wind_direction,
    COALESCE(w.wind_speed, 0) AS wind_speed
FROM temperatures t
LEFT JOIN humidity h ON t.extracted_at = h.extracted_at AND t.hour_index = h.hour_index AND t.forecast_date = h.forecast_date
LEFT JOIN sky_conditions s ON t.extracted_at = s.extracted_at AND t.hour_index = s.hour_index AND t.forecast_date = s.forecast_date
LEFT JOIN wind w ON t.extracted_at = w.extracted_at AND t.hour_index = w.hour_index AND t.forecast_date = w.forecast_date
