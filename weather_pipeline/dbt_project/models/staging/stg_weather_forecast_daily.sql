{{ config(
    materialized = 'view'
) }}

WITH forecast_data AS (
    SELECT
        PROXIMOS_DIAS AS forecast_days,
        _AIRBYTE_EXTRACTED_AT AS extracted_at
    FROM {{ source('raw', 'PALMA') }}
)

SELECT
    extracted_at,
    forecast_date,
    max_temp,
    min_temp,
    max_humidity,
    min_humidity,
    -- Interpolate precipitation_probability
    COALESCE(
        precipitation_probability,
        (PREV_PRECIP + NEXT_PRECIP) / 2,
        0
    ) AS precipitation_probability,
    -- Interpolate sky_condition using previous non-null value
    COALESCE(
        sky_condition,
        PREV_SKY
    ) AS sky_condition,
    -- Interpolate uv_index
    COALESCE(
        uv_index,
        (PREV_UV + NEXT_UV) / 2,
        0
    ) AS uv_index
FROM (
    SELECT
        extracted_at,
        f.value:"@attributes":fecha::STRING AS forecast_date,
        f.value:temperatura:maxima::NUMBER(4,1) AS max_temp,
        f.value:temperatura:minima::NUMBER(4,1) AS min_temp,
        f.value:humedad_relativa:maxima::NUMBER(4,1) AS max_humidity,
        f.value:humedad_relativa:minima::NUMBER(4,1) AS min_humidity,
        f.value:prob_precipitacion[0]::NUMBER AS precipitation_probability,
        f.value:estado_cielo_descripcion[0]::STRING AS sky_condition,
        f.value:uv_max::NUMBER AS uv_index,
        -- Previous and next non-null for interpolation
        LAG(f.value:prob_precipitacion[0]::NUMBER) IGNORE NULLS OVER (ORDER BY f.value:"@attributes":fecha::STRING) AS PREV_PRECIP,
        LEAD(f.value:prob_precipitacion[0]::NUMBER) IGNORE NULLS OVER (ORDER BY f.value:"@attributes":fecha::STRING) AS NEXT_PRECIP,
        LAG(f.value:estado_cielo_descripcion[0]::STRING) IGNORE NULLS OVER (ORDER BY f.value:"@attributes":fecha::STRING) AS PREV_SKY,
        LAG(f.value:uv_max::NUMBER) IGNORE NULLS OVER (ORDER BY f.value:"@attributes":fecha::STRING) AS PREV_UV,
        LEAD(f.value:uv_max::NUMBER) IGNORE NULLS OVER (ORDER BY f.value:"@attributes":fecha::STRING) AS NEXT_UV
    FROM forecast_data,
    LATERAL FLATTEN(input => forecast_days) f
)
