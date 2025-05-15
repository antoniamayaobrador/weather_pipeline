from dagster_dbt import DbtProject
from pathlib import Path

weather_dbt_project = DbtProject(
    name="weather_project",
    project_dir=Path(__file__).joinpath("..", "..", "dbt-weather-project").resolve(),
    profiles_dir=Path(__file__).joinpath("..", "..", "dbt-weather-project").resolve(),  # Adjust this if needed
    profile="prod",  # Ensure this matches your profile name
)