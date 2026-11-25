import dataclasses
import enum

from dtu_hpc_cli.client import get_client


class JobsStats(enum.StrEnum):
    cpu = "cpu"
    memory = "memory"


@dataclasses.dataclass
class JobsConfig:
    node: str | None
    queue: str | None
    stats: JobsStats | None
    full_name: bool = True


CPU_FIELDS = ["cpu_used", "run_time", "nexec_host", "slots"]
MEMORY_FIELDS = ["mem", "max_mem", "avg_mem", "memlimit"]


def execute_jobs(config: JobsConfig):
    command = ["bjobs"]

    # In -o format, a bare field name has unlimited width while "field:" uses the recommended (truncated) width.
    job_name_field = "job_name" if config.full_name else "job_name:"
    base_fields = ["jobid", job_name_field, "stat", "queue", "exec_host"]

    match config.stats:
        case JobsStats.cpu:
            fields = base_fields + CPU_FIELDS
        case JobsStats.memory:
            fields = base_fields + MEMORY_FIELDS
        case _:
            fields = None

    if fields is not None:
        # Single quotes because the SSH client wraps the command in double quotes.
        command.extend(["-o", f"'{' '.join(fields)}'"])
    elif config.full_name:
        # Wide format prevents bjobs from truncating the job name (and other fields) in the default output.
        command.append("-w")

    if config.node is not None:
        command.extend(["-m", config.node])

    if config.queue is not None:
        command.extend(["-q", config.queue])

    command = " ".join(command)

    with get_client() as client:
        client.run(command)
