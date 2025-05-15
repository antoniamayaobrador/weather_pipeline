from dagster import Definitions
from weather_pipeline.assets import airbyte_then_dbt, daily_8am_schedule

defs = Definitions(
    jobs=[airbyte_then_dbt],
    schedules=[daily_8am_schedule],
)
