from dagster import Definitions
from dagster_dbt import DbtCliResource
from .assets import weather_project_dbt_assets
from .project import weather_project_project
from .schedules import schedules

defs = Definitions(
    assets=[weather_project_dbt_assets],
    schedules=schedules,
    resources={
        "dbt": DbtCliResource(project_dir=weather_project_project),
    },
)

