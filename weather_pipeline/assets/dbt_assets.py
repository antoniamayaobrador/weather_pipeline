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


@dbt_assets(manifest=dbt_manifest_path)
def dbt_warehouse(context: AssetExecutionContext, dbt_warehouse_resource: DbtCliResource):
    yield from dbt_warehouse_resource.cli(["run"], context=context).stream()