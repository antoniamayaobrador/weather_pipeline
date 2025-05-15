from setuptools import find_packages, setup

setup(
    name="weather_pipeline",
    packages=find_packages(exclude=["weather_pipeline_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "pandas",
        "pg8000",
        "dagster-airbyte",
        "dagster-dbt",
        "dbt-core==1.7.2",
        "dbt-snowflake==1.7.2",
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
