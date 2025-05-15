import os
import time
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv
from dagster import op, job, ScheduleDefinition


# --- Configuración general ---
AIRBYTE_BASE_URL = "http://airbyte.15.237.180.14.nip.io"
CONNECTION_ID = "fc0fcd97-4a8f-42ea-bfbb-3a393c4325f8"


@op
def sync_airbyte_connection():
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    sync_url = f"{AIRBYTE_BASE_URL}/api/v1/connections/sync"
    payload = {"connectionId": CONNECTION_ID}
    response = requests.post(sync_url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"[ERROR] Airbyte sync failed: {response.status_code} - {response.text}")

    job_id = response.json().get("job", {}).get("id")
    if not job_id:
        raise Exception("[ERROR] No job ID returned from Airbyte")

    print(f"[INFO] Airbyte sync started. Job ID: {job_id}")

    for _ in range(60):
        status_response = requests.get(
            f"{AIRBYTE_BASE_URL}/api/public/v1/jobs/{job_id}",
            headers=headers
        )
        if status_response.status_code != 200:
            raise Exception(f"[ERROR] Failed to fetch job status: {status_response.status_code} - {status_response.text}")

        job_status = status_response.json().get("status")
        print(f"[INFO] Job status: {job_status}")
        if job_status in ("succeeded", "failed", "cancelled", "incomplete"):
            if job_status != "succeeded":
                raise Exception(f"[ERROR] Airbyte job ended with status: {job_status}")
            print("[SUCCESS] Airbyte sync completed successfully.")
            return str(job_id)
        time.sleep(5)

    raise Exception("[TIMEOUT] Airbyte sync did not finish within expected time.")


@op
def prepare_dbt_project_dir(context):
    dbt_path = Path(__file__).parent / "dbt_project"
    context.log.info(f"[DEBUG] Checking DBT project at: {dbt_path.resolve()}")

    if not dbt_path.exists():
        raise Exception(f"[ERROR] DBT project not found at: {dbt_path.resolve()}")

    # Copiar .env si es necesario
    local_env = Path(__file__).parent / ".env"
    dbt_project_env = dbt_path / ".env"

    if local_env.exists():
        context.log.info(f"[INFO] Copying .env from {local_env} to {dbt_project_env}")
        if not dbt_project_env.exists():
            subprocess.run(["cp", str(local_env), str(dbt_project_env)])

    return str(dbt_path.resolve())


@op
def run_dbt(context, dbt_project_dir: str, sync_result: str):
    # Cargar variables del .env
    dotenv_path = Path(__file__).parent / ".env"
    context.log.info(f"[INFO] Looking for .env at: {dotenv_path.resolve()}")

    if not dotenv_path.exists():
        raise Exception(f"[ERROR] .env file not found at {dotenv_path.resolve()}")

    load_dotenv(dotenv_path=dotenv_path)

    # Comprobar variables necesarias
    required_vars = [
        "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_DATABASE", "SNOWFLAKE_WAREHOUSE"
    ]
    for var in required_vars:
        val = os.getenv(var)
        context.log.info(f"[ENV] {var}={val}")
        if not val:
            raise Exception(f"[ERROR] Environment variable {var} is not defined in the .env file.")

    profiles_path = Path(dbt_project_dir) / "profiles.yml"
    if not profiles_path.exists():
        raise Exception(f"[ERROR] profiles.yml not found at {profiles_path.resolve()}")

    cmd = [
        "dbt", "build",
        "--project-dir", dbt_project_dir,
        "--profile", "prod",
        "--target", "prod",
        "--profiles-dir", dbt_project_dir
    ]

    context.log.info(f"[DBT COMMAND] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    context.log.info("[DBT STDOUT]")
    context.log.info(result.stdout)
    context.log.info("[DBT STDERR]")
    context.log.info(result.stderr)

    if result.returncode != 0:
        error_log_path = Path(dbt_project_dir) / "dbt_error_log.txt"
        with open(error_log_path, "w") as f:
            f.write("STDOUT:\n" + result.stdout)
            f.write("\n\nSTDERR:\n" + result.stderr)

        context.log.error(f"[DBT ERROR] Full error saved at {error_log_path}")
        raise Exception("[ERROR] dbt build failed.")


@job
def airbyte_then_dbt():
    sync_result = sync_airbyte_connection()
    dbt_project_dir = prepare_dbt_project_dir()
    run_dbt(dbt_project_dir=dbt_project_dir, sync_result=sync_result)


daily_8am_schedule = ScheduleDefinition(
    job=airbyte_then_dbt,
    cron_schedule="0 8 * * *",
    execution_timezone="Europe/Madrid",
    name="daily_8am_weather_pipeline",
)
