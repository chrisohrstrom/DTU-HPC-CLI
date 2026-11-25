import dataclasses

import typer

from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.history import load_history


@dataclasses.dataclass
class RemoveConfig:
    all: bool
    from_history: bool
    job_ids: list[str]


def execute_remove(config: RemoveConfig):
    job_ids = expand_job_ids(config)
    with get_client() as client:
        for job_id in job_ids:
            client.run(f"bkill {job_id}")


def expand_job_ids(config: RemoveConfig) -> list[str]:
    if config.all:
        job_ids = get_all_job_ids()
        if len(job_ids) == 0:
            typer.echo("No jobs to remove.")
            raise typer.Exit()
        typer.echo("The following jobs will be removed (because --all flag is used):")
        for job_id in job_ids:
            typer.echo(f" * {job_id}")
        typer.confirm("\nRemove all jobs (enter to remove)?", abort=True, default=True)
        return job_ids

    if not config.from_history:
        return config.job_ids

    history = load_history()
    requested_ids = set(config.job_ids)

    job_ids = requested_ids.copy()
    for entry in history:
        entry_job_ids = set(entry["job_ids"])
        if not entry_job_ids.isdisjoint(requested_ids):
            job_ids.update(entry_job_ids)

    new_job_ids = job_ids - requested_ids
    job_ids = sorted(job_ids)
    if len(new_job_ids) != 0:
        typer.echo("The following jobs will be removed (because --from-history flag is used):")
        for job_id in job_ids:
            typer.echo(f" * {job_id}")
        typer.confirm("\nRemove these jobs (enter to remove)?", abort=True, default=True)

    return job_ids


def get_all_job_ids() -> list[str]:
    with get_client() as client:
        _, output = client.run("bjobs -noheader -o jobid", silent=True)

    # bjobs prints "No unfinished job found" (possibly merged into stdout) when there are no jobs,
    # so only keep lines that are actual job IDs.
    job_ids = [line.strip() for line in output.splitlines() if line.strip().isdigit()]

    return job_ids
