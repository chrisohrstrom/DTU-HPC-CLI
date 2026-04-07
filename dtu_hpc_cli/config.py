import dataclasses
import json
from hashlib import sha256
from pathlib import Path

from git import Repo

from dtu_hpc_cli.constants import CONFIG_FILENAME
from dtu_hpc_cli.constants import HISTORY_FILENAME
from dtu_hpc_cli.error import error_and_exit
from dtu_hpc_cli.types import Date
from dtu_hpc_cli.types import Duration
from dtu_hpc_cli.types import Memory
from dtu_hpc_cli.types import Time

ACTIVE_BRANCH_KEY = "[[active_branch]]"

DEFAULT_HOSTNAME = "login1.hpc.dtu.dk"

DEFAULT_SUBMIT_BRANCH = "main"


@dataclasses.dataclass
class InstallConfig:
    commands: list[str]
    sync: bool

    @classmethod
    def load(cls, config: dict):
        if "install" not in config:
            return None

        install = config["install"]
        install = InstallConfig.validate(install)

        if "commands" not in install:
            error_and_exit('"commands" not found in install config.')

        if "sync" not in install:
            install["sync"] = True

        return cls(**install)

    @classmethod
    def validate(cls, config: dict) -> dict:
        if isinstance(config, list):
            # We support this configuration for backwards compatibility
            return {"commands": config}

        if not isinstance(config, dict):
            error_and_exit(f"Invalid type for install option in config. Expected dictionary but got {type(config)}.")

        output = {}

        commands = config.get("commands")
        if commands is not None:
            if not isinstance(commands, list):
                error_and_exit(
                    f"Invalid type for commands option in install config. Expected list but got {type(commands)}."
                )
            output["commands"] = commands

        sync = config.get("sync")
        if sync is not None:
            if not isinstance(sync, bool):
                error_and_exit(
                    f"Invalid type for sync option in install config. Expected boolean but got {type(sync)}."
                )
            output["sync"] = sync

        return output


@dataclasses.dataclass
class SSHConfig:
    hostname: str
    user: str
    identityfile: str

    @classmethod
    def load(cls, config: dict):
        if "ssh" not in config:
            return None

        ssh = config["ssh"]
        ssh = SSHConfig.validate(ssh)

        if "hostname" not in ssh:
            ssh["hostname"] = DEFAULT_HOSTNAME

        if "user" not in ssh:
            error_and_exit('"user" not found in SSH config.')

        if "identityfile" not in ssh:
            error_and_exit('"identityfile" not found in SSH config')

        return cls(**ssh)

    @classmethod
    def validate(cls, config: dict) -> dict:
        if not isinstance(config, dict):
            error_and_exit(f"Invalid type for ssh option in config. Expected dictionary but got {type(config)}.")

        output = {}

        hostname = config.get("hostname")
        if hostname is not None:
            if not isinstance(hostname, str):
                error_and_exit(f"Invalid type for host option in ssh config. Expected string but got {type(hostname)}.")
            output["hostname"] = hostname

        user = config.get("user")
        if user is not None:
            if not isinstance(user, str):
                error_and_exit(f"Invalid type for user option in ssh config. Expected string but got {type(user)}.")
            output["user"] = user

        identityfile = config.get("identityfile")
        if identityfile is not None:
            if not isinstance(identityfile, str):
                error_and_exit(
                    f"Invalid type for identityfile option in ssh config. Expected string but got {type(identityfile)}."
                )
            output["identityfile"] = identityfile

        return output


@dataclasses.dataclass
class SubmitConfig:
    branch: str | None
    commands: list[str]
    confirm: bool
    cores: int
    email: str | None
    feature: list[str] | None
    error: str | None
    gpus: int | None
    hosts: int
    memory: Memory
    model: str | None
    notify_begin: bool
    notify_end: bool
    notify_fail: bool
    name: str
    output: str | None
    queue: str
    preamble: list[str]
    split_every: Duration
    start_after: str | None
    sync: bool
    walltime: Duration
    date: Date | None = None
    time: Time | None = None

    @classmethod
    def defaults(cls):
        return {
            "branch": ACTIVE_BRANCH_KEY,
            "commands": [],
            "confirm": True,
            "cores": 4,
            "date": None,
            "email": None,
            "feature": None,
            "error": None,
            "gpus": None,
            "hosts": 1,
            "memory": "5GB",
            "model": None,
            "name": "NONAME",
            "notify_begin": False,
            "notify_end": False,
            "notify_fail": True,
            "output": None,
            "queue": "hpc",
            "preamble": [],
            "split_every": "1d",
            "start_after": None,
            "sync": True,
            "time": None,
            "walltime": "1d",
        }

    @classmethod
    def load(cls, config: dict, project_root: Path):
        if "submit" not in config:
            submit = cls.defaults()
        else:
            submit = config["submit"]
            submit = {key.replace("-", "_"): value for key, value in submit.items()}
            submit = {**cls.defaults(), **submit}

        submit = cls.validate(submit, project_root)

        return submit

    @classmethod
    def validate(cls, config: dict, project_root: Path) -> dict:
        if not isinstance(config, dict):
            error_and_exit(f"Invalid type for submit option in config. Expected dictionary but got {type(config)}.")

        output = {key.replace("-", "_"): value for key, value in config.items()}
        for key in output.keys():
            if key not in cls.__annotations__:
                error_and_exit(f"Unknown option in submit config: {key}")

        branch = output.get("branch")
        if branch == ACTIVE_BRANCH_KEY:
            with Repo(project_root) as repo:
                output["branch"] = repo.active_branch.name

        return output

    def to_dict(self):
        return {
            "branch": self.branch,
            "commands": self.commands,
            "confirm": self.confirm,
            "cores": self.cores,
            "date": str(self.date) if self.date is not None else None,
            "email": self.email,
            "feature": self.feature,
            "error": self.error,
            "gpus": self.gpus,
            "hosts": self.hosts,
            "memory": str(self.memory),
            "model": self.model,
            "name": self.name,
            "notify_begin": self.notify_begin,
            "notify_end": self.notify_end,
            "notify_fail": self.notify_fail,
            "output": self.output,
            "queue": self.queue,
            "preamble": self.preamble,
            "split_every": str(self.split_every),
            "start_after": self.start_after,
            "sync": self.sync,
            "time": str(self.time) if self.time is not None else None,
            "walltime": str(self.walltime),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            branch=data["branch"],
            commands=data["commands"],
            confirm=data.get("confirm", True),
            cores=data["cores"],
            date=Date.parse(data["date"]) if "date" in data else None,
            email=data.get("email", None),
            feature=data["feature"],
            error=data["error"],
            gpus=data["gpus"],
            hosts=data["hosts"],
            memory=Memory.parse(data["memory"]),
            model=data["model"],
            name=data["name"],
            notify_begin=data.get("notify_begin", False),
            notify_end=data.get("notify_end", False),
            notify_fail=data.get("notify_fail", False),
            output=data["output"],
            queue=data["queue"],
            preamble=data["preamble"],
            split_every=Duration.parse(data["split_every"]),
            start_after=data["start_after"],
            sync=data.get("sync", True),
            time=Time.parse(data["time"]) if "time" in data else None,
            walltime=Duration.parse(data["walltime"]),
        )


@dataclasses.dataclass
class CLIConfig:
    history_path: Path
    install: InstallConfig | None
    modules: list[str] | None
    project_root: Path
    remote_path: str
    profiles: dict | None
    ssh: SSHConfig | None
    submit: SubmitConfig | None

    @classmethod
    def load(cls):
        project_root = cls.get_project_root()

        git_path = project_root / ".git"
        if not git_path.exists():
            error_and_exit(f"Could not find git repository at '{git_path}'.")

        path = project_root / CONFIG_FILENAME

        try:
            config = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            error_and_exit(f"Error while parsing config file at '{path}':\n{e}")

        if not isinstance(config, dict):
            error_and_exit(f"Invalid type for config. Expected dictionary but got {type(config)}.")

        profiles = config.get("profiles")
        if profiles is not None and not isinstance(profiles, dict):
            error_and_exit(f"Invalid type for profiles option in config. Expected dictionary but got {type(profiles)}.")

        history_path = cls.load_history_path(config, project_root)
        install = InstallConfig.load(config)
        modules = cls.load_modules(config)
        remote_path = cls.load_remote_path(config, project_root)
        ssh = SSHConfig.load(config)
        submit = SubmitConfig.load(config, project_root)

        return cls(
            history_path=history_path,
            install=install,
            modules=modules,
            profiles=profiles,
            project_root=project_root,
            remote_path=remote_path,
            ssh=ssh,
            submit=submit,
        )

    @classmethod
    def get_project_root(cls) -> Path:
        """Assume that config file exist in the project root and use that to get the project root."""
        root = Path("/")
        current_path = Path.cwd()
        while current_path != root:
            if (current_path / CONFIG_FILENAME).exists():
                return current_path
            current_path = current_path.parent

        if (root / CONFIG_FILENAME).exists():
            return root

        error_and_exit(
            f"Could not find project root. Make sure that '{CONFIG_FILENAME}' exists in the root of the project."
        )

    @classmethod
    def load_history_path(cls, config: dict, project_root: Path) -> Path:
        if "history_path" in config:
            history_path = config["history_path"]
            if not isinstance(history_path, str):
                error_and_exit(
                    f"Invalid type for history_path option in config. Expected string but got {type(history_path)}."
                )
            return Path(history_path)
        return project_root / HISTORY_FILENAME

    @classmethod
    def load_modules(cls, config: dict) -> list[str] | None:
        if "modules" in config:
            modules = config["modules"]
            if not isinstance(modules, list):
                error_and_exit(f"Invalid type for modules option in config. Expected list but got {type(modules)}.")
            for i, module in enumerate(modules):
                if not isinstance(module, str):
                    error_and_exit(
                        f"Invalid type for module at index {i} in config. Expected string but got {type(module)}."
                    )
            return modules
        return None

    @classmethod
    def load_remote_path(cls, config: dict, project_root: Path) -> str:
        if "remote_path" in config:
            return config["remote_path"]

        name = project_root.name
        hash = sha256(str(project_root).encode()).hexdigest()[:8]
        return f"~/{name}-{hash}"

    def check_ssh(self, msg: str = "SSH configuration is required for this command."):
        if self.ssh is None:
            error_and_exit(msg)

    def load_profile(self, name: str):
        if name not in self.profiles:
            error_and_exit(f"Profile '{name}' not found in config.")

        profile = self.profiles[name]

        if "history_path" in profile:
            self.history_path = CLIConfig.load_history_path(profile, self.project_root)

        if "install" in profile:
            install = InstallConfig.validate(profile["install"])
            self.install = dataclasses.replace(self.install, **install)

        if "modules" in profile:
            self.modules = profile["modules"]

        if "remote_path" in profile:
            self.remote_path = profile["remote_path"]

        if "ssh" in profile:
            ssh = SSHConfig.validate(profile["ssh"])
            self.ssh = dataclasses.replace(self.ssh, **ssh)

        if "submit" in profile:
            submit = SubmitConfig.validate(profile["submit"], self.project_root)
            self.submit = {**self.submit, **submit}


cli_config = CLIConfig.load()
