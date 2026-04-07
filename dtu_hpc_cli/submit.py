import dataclasses
import os
import re
from datetime import datetime
from uuid import uuid4

import typer

from dtu_hpc_cli.client import Client
from dtu_hpc_cli.client import get_client
from dtu_hpc_cli.config import SubmitConfig
from dtu_hpc_cli.config import cli_config
from dtu_hpc_cli.error import error_and_exit
from dtu_hpc_cli.history import add_to_history
from dtu_hpc_cli.sync import check_and_confirm_changes
from dtu_hpc_cli.sync import execute_sync
from dtu_hpc_cli.types import Date
from dtu_hpc_cli.types import Time

JOB_ID_PATTERN = re.compile(r"Job <([\d]+)> is submitted to queue")


def execute_submit(submit_config: SubmitConfig):
    if submit_config.sync:
        check_and_confirm_changes()

    if submit_config.walltime > submit_config.split_every:
        typer.echo(
            f"This will result in multiple jobs as the split time is '{submit_config.split_every}' "
            + f"and the walltime '{submit_config.walltime}' exceeds that limit."
        )

    script = create_job_script(submit_config)
    if submit_config.confirm:
        typer.echo("Job script:")
        typer.echo(f"\n{script}\n")
        typer.confirm("Submit job (enter to submit)?", default=True, abort=True)

    if submit_config.sync:
        execute_sync(confirm_changes=False)

    typer.echo("Submitting job...")

    # add date to the config for history
    submit_config.date = Date(datetime.now().date())
    submit_config.time = Time(datetime.now().time())

    if submit_config.walltime > submit_config.split_every:
        submit_multiple(submit_config)
    else:
        submit_once(submit_config)


def submit_once(submit_config: SubmitConfig):
    with get_client() as client:
        job_id = submit(client, submit_config)
    add_to_history(submit_config, [job_id])


def submit_multiple(submit_config: SubmitConfig):
    job_ids = []
    with get_client() as client:
        start_after = submit_config.start_after
        job_counter = 1
        time_left = submit_config.walltime
        while not time_left.is_zero():
            job_name = f"{submit_config.name}-{job_counter}"
            job_walltime = time_left if time_left < submit_config.split_every else submit_config.split_every
            job_config = dataclasses.replace(
                submit_config, name=job_name, start_after=start_after, walltime=job_walltime
            )
            job_id = submit(client, job_config)
            job_ids.append(job_id)
            start_after = job_id
            job_counter += 1
            time_left -= job_walltime
    add_to_history(submit_config, job_ids)


def submit(client: Client, submit_config: SubmitConfig) -> str:
    job_script = create_job_script(submit_config)
    path = f"/tmp/{uuid4()}.sh"
    client.save(path, job_script)
    returncode, stdout = client.run(f"bsub < {path}", cwd=cli_config.remote_path)
    client.remove(path)

    if returncode != 0:
        error_and_exit(f"Submission command failed with return code {returncode}.")

    job_ids = JOB_ID_PATTERN.findall(stdout)
    if len(job_ids) != 1:
        error_and_exit(stdout)
    job_id = job_ids[0]
    return job_id


def create_job_script(config: SubmitConfig) -> str:
    modules = []
    if cli_config.modules is not None:
        modules = [f"module load {module}" for module in cli_config.modules]
        modules.insert(0, "")
        modules.insert(1, "# Modules")

    preamble = []
    for command in config.preamble:
        command = prepare_command(config, command)
        preamble.append(command)
    if len(preamble) > 0:
        preamble.insert(0, "")
        preamble.insert(1, "# Preamble")

    commands = []
    for command in config.commands:
        command = prepare_command(config, command)
        commands.append(command)

    options = [
        ("J", config.name),
        ("q", config.queue),
        ("n", config.cores),
        ("R", f"rusage[mem={config.memory}]"),
        ("R", f"span[hosts={config.hosts}]"),
        ("W", f"{config.walltime.total_hours():02d}:{config.walltime.minutes:02d}"),
    ]

    if config.gpus is not None and config.gpus > 0:
        options.append(("gpu", f"num={config.gpus}:mode=exclusive_process"))

    if config.start_after is not None:
        options.append(("w", f"ended({config.start_after})"))

    if config.error is not None:
        error_path = os.path.join(config.error, f"{config.name}_%J.err")
        options.append(("e", error_path))

    if config.output is not None:
        output_path = os.path.join(config.output, f"{config.name}_%J.out")
        options.append(("o", output_path))

    if config.model is not None:
        options.append(("R", f'"select[model == {config.model}]"'))

    features = [] if config.feature is None else config.feature
    for feature in features:
        options.append(("R", f'"select[{feature}]"'))

    if config.email is not None:
        options.append(("u", config.email))

    options = [f"#BSUB -{flag} {value}" for flag, value in options]

    if config.notify_begin or config.notify_end or config.notify_fail:
        if config.notify_begin:
            options.append("#BSUB -B")
        if config.notify_end:
            options.append("#BSUB -N")
        if config.notify_fail:
            options.append("#BSUB -Ne")
    else:
        options.append('#BSUB -env "LSB_JOB_REPORT_MAIL=N"')

    script = [
        "#!/bin/sh",
        "### General options",
        *options,
        "# -- end of LSF options --",
        *modules,
        *preamble,
        "",
        "# Commands",
        *commands,
    ]

    script = "\n".join(script)

    return script


def prepare_command(config: SubmitConfig, command: str):
    command = command.strip()
    if config.branch is not None:
        command = f"git switch {config.branch} && {command}"
    return command
