{{ config(
    materialized = 'view'
) }}

SELECT
    TO_TIMESTAMP_NTZ(FECHA) AS date_time,
    CAST(TEMPERATURA_ACTUAL AS NUMBER(4,1)) AS temperature,
    CAST(HUMEDAD AS NUMBER(4,1)) AS humidity,
    CAST(VIENTO AS NUMBER(4,1)) AS wind_speed,
    STATESKY:description::STRING AS sky_condition,
    _AIRBYTE_EXTRACTED_AT AS extracted_at
FROM {{ source('raw', 'PALMA') }}
