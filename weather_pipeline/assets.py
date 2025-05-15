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


from dagster_dbt import DbtCliResource
from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets

# configure dbt project resource
dbt_project_dir = Path(__file__).joinpath("../dbt_project").resolve()
dbt_warehouse_resource = DbtCliResource(project_dir=os.fspath(dbt_project_dir))

# generate manifest
dbt_manifest_path = (
    dbt_warehouse_resource.cli(
        ["--quiet", "parse"],
        target_path=Path("target"),
    )
    .wait()
    .target_path.joinpath("manifest.json")
)

# load manifest to produce asset defintion
@dbt_assets(manifest=dbt_manifest_path)
def dbt_warehouse(context: AssetExecutionContext, dbt_warehouse_resource: DbtCliResource):
    yield from dbt_warehouse_resource.cli(["run"], context=context).stream()

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
