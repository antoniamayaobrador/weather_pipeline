from pathlib import Path

from dagster_dbt import DbtProject

weather_project_project = DbtProject(
    project_dir=Path(__file__).joinpath("..", "..", "..").resolve(),
    packaged_project_dir=Path(__file__).joinpath("..", "..", "dbt-project").resolve(),
)
weather_project_project.prepare_if_dev()

