from typing import List

import typer
from typing_extensions import Annotated

from dtu_hpc_cli.config import SubmitConfig
from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.constants import CONFIG_FILENAME
from dtu_hpc_cli.get_command import execute_get_command
from dtu_hpc_cli.get_options import Option
from dtu_hpc_cli.get_options import execute_get_options
from dtu_hpc_cli.history import HistoryConfig
from dtu_hpc_cli.history import execute_history
from dtu_hpc_cli.install import execute_install
from dtu_hpc_cli.jobs import JobsConfig
from dtu_hpc_cli.jobs import JobsStats
from dtu_hpc_cli.jobs import execute_jobs
from dtu_hpc_cli.open_error import execute_open_error
from dtu_hpc_cli.open_output import execute_open_output
from dtu_hpc_cli.queues import execute_queues
from dtu_hpc_cli.remove import RemoveConfig
from dtu_hpc_cli.remove import execute_remove
from dtu_hpc_cli.resubmit import ResubmitConfig
from dtu_hpc_cli.resubmit import execute_resubmit
from dtu_hpc_cli.run import execute_run
from dtu_hpc_cli.start_time import StartTimeConfig
from dtu_hpc_cli.start_time import execute_start_time
from dtu_hpc_cli.stats import StatsConfig
from dtu_hpc_cli.stats import execute_stats
from dtu_hpc_cli.submit import execute_submit
from dtu_hpc_cli.sync import execute_sync
from dtu_hpc_cli.types import Date
from dtu_hpc_cli.types import Duration
from dtu_hpc_cli.types import Memory
from dtu_hpc_cli.types import Time

__version__ = "1.5.1"

cli = typer.Typer(pretty_exceptions_show_locals=False)


class SubmitDefault:
    def __init__(self, key: str):
        self.key = key

    def __call__(self):
        return cli_config.submit.get(self.key)

    def __str__(self):
        value = cli_config.submit.get(self.key)
        return str(value)


def profile_callback(profile: str | None):
    if profile is not None:
        cli_config.load_profile(profile)


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@cli.callback()
def main(
    profile: Annotated[
        str, typer.Option("--profile", callback=profile_callback, help="Optional profile from config.")
    ] = None,
    version: Annotated[bool, typer.Option("--version", callback=version_callback)] = False,
):
    pass


@cli.command()
def get_command(job_id: str):
    """Get the command used to submit a previous job."""
    execute_get_command(job_id)


@cli.command()
def get_options(job_id: str, options: List[Option]):
    """Print options from a previously submitted job."""
    execute_get_options(job_id, options)


@cli.command()
def history(
    branch: bool = True,
    branch_contains: str | None = None,
    branch_is: str | None = None,
    commands: bool = True,
    command_contains: str | None = None,
    command_is: str | None = None,
    confirm: bool = False,
    cores: bool = True,
    cores_above: int | None = None,
    cores_below: int | None = None,
    cores_is: int | None = None,
    date: bool = True,
    date_after: Annotated[Date, typer.Option(parser=Date.parse)] = None,
    date_before: Annotated[Date, typer.Option(parser=Date.parse)] = None,
    date_is: Annotated[Date, typer.Option(parser=Date.parse)] = None,
    feature: bool = False,
    feature_contains: str | None = None,
    feature_is: str | None = None,
    error: bool = False,
    error_contains: str | None = None,
    error_is: str | None = None,
    gpus: bool = True,
    gpus_above: int | None = None,
    gpus_below: int | None = None,
    gpus_is: int | None = None,
    hosts: bool = False,
    hosts_above: int | None = None,
    hosts_below: int | None = None,
    hosts_is: int | None = None,
    limit: int = 5,
    memory: bool = True,
    memory_above: Annotated[Memory, typer.Option(parser=Memory.parse)] = None,
    memory_below: Annotated[Memory, typer.Option(parser=Memory.parse)] = None,
    memory_is: Annotated[Memory, typer.Option(parser=Memory.parse)] = None,
    model: bool = False,
    model_contains: str | None = None,
    model_is: str | None = None,
    name: bool = True,
    name_contains: str | None = None,
    name_is: str | None = None,
    output: bool = False,
    output_contains: str | None = None,
    output_is: str | None = None,
    queue: bool = True,
    queue_contains: str | None = None,
    queue_is: str | None = None,
    preamble: bool = False,
    preamble_contains: str | None = None,
    preamble_is: str | None = None,
    split_every: bool = False,
    split_every_above: Annotated[Duration, typer.Option(parser=Duration.parse)] = None,
    split_every_below: Annotated[Duration, typer.Option(parser=Duration.parse)] = None,
    split_every_is: Annotated[Duration, typer.Option(parser=Duration.parse)] = None,
    start_after: bool = False,
    start_after_contains: str | None = None,
    start_after_is: str | None = None,
    sync: bool = False,
    time: bool = True,
    time_after: Annotated[Time, typer.Option(parser=Time.parse)] = None,
    time_before: Annotated[Time, typer.Option(parser=Time.parse)] = None,
    time_is: Annotated[Time, typer.Option(parser=Time.parse)] = None,
    walltime: bool = True,
    walltime_above: Annotated[Duration, typer.Option(parser=Duration.parse)] = None,
    walltime_below: Annotated[Duration, typer.Option(parser=Duration.parse)] = None,
    walltime_is: Annotated[Duration, typer.Option(parser=Duration.parse)] = None,
):
    """Show the history of submitted jobs."""
    config = HistoryConfig(
        branch=branch,
        branch_contains=branch_contains,
        branch_is=branch_is,
        commands=commands,
        command_contains=command_contains,
        command_is=command_is,
        confirm=confirm,
        cores=cores,
        cores_above=cores_above,
        cores_below=cores_below,
        cores_is=cores_is,
        date=date,
        date_after=date_after,
        date_before=date_before,
        date_is=date_is,
        feature=feature,
        feature_contains=feature_contains,
        feature_is=feature_is,
        error=error,
        error_contains=error_contains,
        error_is=error_is,
        gpus=gpus,
        gpus_above=gpus_above,
        gpus_below=gpus_below,
        gpus_is=gpus_is,
        hosts=hosts,
        hosts_above=hosts_above,
        hosts_below=hosts_below,
        hosts_is=hosts_is,
        limit=limit,
        memory=memory,
        memory_above=memory_above,
        memory_below=memory_below,
        memory_is=memory_is,
        model=model,
        model_contains=model_contains,
        model_is=model_is,
        name=name,
        name_contains=name_contains,
        name_is=name_is,
        output=output,
        output_contains=output_contains,
        output_is=output_is,
        queue=queue,
        queue_contains=queue_contains,
        queue_is=queue_is,
        preamble=preamble,
        preamble_contains=preamble_contains,
        preamble_is=preamble_is,
        split_every=split_every,
        split_every_above=split_every_above,
        split_every_below=split_every_below,
        split_every_is=split_every_is,
        start_after=start_after,
        start_after_contains=start_after_contains,
        start_after_is=start_after_is,
        sync=sync,
        time=time,
        time_after=time_after,
        time_before=time_before,
        time_is=time_is,
        walltime=walltime,
        walltime_above=walltime_above,
        walltime_below=walltime_below,
        walltime_is=walltime_is,
    )
    execute_history(config)


@cli.command()
def install():
    """Run the install script in the remote directory on the HPC."""
    execute_install()


@cli.command()
def jobs(
    node: str | None = None,
    queue: str | None = None,
    stats: Annotated[JobsStats, typer.Option()] = None,
):
    """List running and pending jobs."""
    list_config = JobsConfig(node=node, queue=queue, stats=stats)
    execute_jobs(list_config)


@cli.command()
def open_error(job_id: str):
    """Show the job error in your editor."""
    execute_open_error(job_id)


@cli.command()
def open_output(job_id: str):
    """Show the job output in your editor."""
    execute_open_output(job_id)


@cli.command()
def queues(queue: Annotated[str, typer.Argument()] = None):
    """List available queues."""
    execute_queues(queue)


@cli.command()
def remove(
    job_ids: Annotated[List[str], typer.Argument()] = None,
    all_jobs: Annotated[bool, typer.Option("--all")] = False,
    from_history: bool = False,
):
    """Remove jobs from the queue."""
    if not all_jobs and job_ids is None:
        raise typer.BadParameter("Provide job IDs or use --all to remove all jobs.")
    elif all_jobs and job_ids is not None:
        raise typer.BadParameter("Cannot provide job IDs when using --all.")

    if job_ids is None:
        job_ids = []
    config = RemoveConfig(all=all_jobs, from_history=from_history, job_ids=job_ids)
    execute_remove(config)


@cli.command()
def resubmit(
    job_id: str,
    branch: str = None,
    command: List[str] = None,
    confirm: bool = None,
    cores: int = None,
    email: str = None,
    error: str = None,
    feature: List[str] = None,
    gpus: int = None,
    hosts: int = None,
    memory: Annotated[Memory, typer.Option(parser=Memory.parse)] = None,
    model: str = None,
    name: str = None,
    notify_begin: bool = None,
    notify_end: bool = None,
    notify_fail: bool = None,
    output: str = None,
    preamble: List[str] = None,
    queue: str = None,
    split_every: Annotated[Duration, typer.Option(parser=Duration.parse)] = None,
    start_after: str = None,
    sync: bool = None,
    walltime: Annotated[Duration, typer.Option(parser=Duration.parse)] = None,
):
    """Resubmit a job. Optionally with new parameters."""
    config = ResubmitConfig(
        job_id=job_id,
        branch=branch,
        commands=command,
        confirm=confirm,
        cores=cores,
        email=email,
        error=error,
        feature=feature,
        gpus=gpus,
        hosts=hosts,
        memory=memory,
        model=model,
        name=name,
        notify_begin=notify_begin,
        notify_end=notify_end,
        notify_fail=notify_fail,
        output=output,
        preamble=preamble,
        queue=queue,
        split_every=split_every,
        start_after=start_after,
        sync=sync,
        walltime=walltime,
    )
    execute_resubmit(config)


@cli.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(ctx: typer.Context):
    """Run a command on the HPC.

    Uses the configured remote path as the working directory."""
    execute_run(ctx.args)


@cli.command()
def start_time(job_ids: Annotated[List[str], typer.Argument()] = None, queue: str = None, user: str = None):
    """Show the start time of pending jobs."""
    config = StartTimeConfig(job_ids=job_ids, queue=queue, user=user)
    execute_start_time(config)


@cli.command()
def stats(
    queue: Annotated[str, typer.Argument()] = None,
    cpu: bool = False,
    gpu: bool = False,
    jobs: bool = False,
    memory: bool = False,
    node: str | None = None,
    reserved: bool = False,
):
    """Show statistics for the queue(s)."""
    config = StatsConfig(
        cpu=cpu,
        gpu=gpu,
        jobs=jobs,
        memory=memory,
        node=node,
        reserved=reserved,
        queue=queue,
    )
    execute_stats(config)


@cli.command()
def submit(
    commands: List[str],
    branch: Annotated[str, typer.Option(default_factory=SubmitDefault("branch"))],
    cores: Annotated[int, typer.Option(default_factory=SubmitDefault("cores"))],
    confirm: Annotated[bool, typer.Option(default_factory=SubmitDefault("confirm"))],
    email: Annotated[str, typer.Option(default_factory=SubmitDefault("email"))],
    error: Annotated[str, typer.Option(default_factory=SubmitDefault("error"))],
    feature: Annotated[List[str], typer.Option(default_factory=SubmitDefault("feature"))],
    gpus: Annotated[int, typer.Option(default_factory=SubmitDefault("gpus"))],
    hosts: Annotated[int, typer.Option(default_factory=SubmitDefault("hosts"))],
    memory: Annotated[Memory, typer.Option(parser=Memory.parse, default_factory=SubmitDefault("memory"))],
    model: Annotated[str, typer.Option(default_factory=SubmitDefault("model"))],
    name: Annotated[str, typer.Option(default_factory=SubmitDefault("name"))],
    notify_begin: Annotated[bool, typer.Option(default_factory=SubmitDefault("notify_begin"))],
    notify_end: Annotated[bool, typer.Option(default_factory=SubmitDefault("notify_end"))],
    notify_fail: Annotated[bool, typer.Option(default_factory=SubmitDefault("notify_fail"))],
    output: Annotated[str, typer.Option(default_factory=SubmitDefault("output"))],
    preamble: Annotated[List[str], typer.Option(default_factory=SubmitDefault("preamble"))],
    queue: Annotated[str, typer.Option(default_factory=SubmitDefault("queue"))],
    split_every: Annotated[Duration, typer.Option(parser=Duration.parse, default_factory=SubmitDefault("split_every"))],
    start_after: Annotated[str, typer.Option(default_factory=SubmitDefault("start_after"))],
    sync: Annotated[bool, typer.Option(default_factory=SubmitDefault("sync"))],
    walltime: Annotated[Duration, typer.Option(parser=Duration.parse, default_factory=SubmitDefault("walltime"))],
):
    """Submit a job to the queue."""
    submit_config = SubmitConfig(
        branch=branch,
        commands=commands,
        confirm=confirm,
        cores=cores,
        email=email,
        error=error,
        feature=feature,
        gpus=gpus,
        hosts=hosts,
        memory=memory,
        model=model,
        name=name,
        notify_begin=notify_begin,
        notify_end=notify_end,
        notify_fail=notify_fail,
        output=output,
        preamble=preamble,
        queue=queue,
        split_every=split_every,
        start_after=start_after,
        sync=sync,
        walltime=walltime,
    )
    execute_submit(submit_config)


@cli.command()
def sync():
    """Sync the local directory with the remote directory on the HPC."""
    cli_config.check_ssh(msg=f"Sync requires a SSH configuration in '{CONFIG_FILENAME}'.")
    execute_sync()


if __name__ == "__main__":
    cli()
