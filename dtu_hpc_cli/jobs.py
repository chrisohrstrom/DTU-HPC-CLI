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


BASE_FIELDS = ["jobid", "job_name", "stat", "queue", "exec_host"]
CPU_FIELDS = ["cpu_used", "run_time", "nexec_host", "slots"]
MEMORY_FIELDS = ["mem", "max_mem", "avg_mem", "memlimit"]


def execute_jobs(config: JobsConfig):
    command = ["bjobs"]
    match config.stats:
        case JobsStats.cpu:
            fields = BASE_FIELDS + CPU_FIELDS
        case JobsStats.memory:
            fields = BASE_FIELDS + MEMORY_FIELDS
        case _:
            fields = None

    if fields is not None:
        # Single quotes because the SSH client wraps the command in double quotes.
        command.extend(["-o", f"'{' '.join(fields)}'"])

    if config.node is not None:
        command.extend(["-m", config.node])

    if config.queue is not None:
        command.extend(["-q", config.queue])

    command = " ".join(command)

    with get_client() as client:
        client.run(command)
