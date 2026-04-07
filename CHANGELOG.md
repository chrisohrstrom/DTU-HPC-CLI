# Changelogs

## v1.5.0

submit and resubmit:
* Added new options to control where and when to get email notifications about jobs: `--email`, `--notify-begin`, `--notify-end`, `--notify-fail`

## v1.4.1

General fixes:
* Will now check for `hostname` (instead of `host`) when validating SSH configs.
* Fixed issue where profiles examples in README were formatted incorrectly.
* Replaced instances of `dtu list` with `dtu jobs` in README.

get-command:
* Fix: List options (e.g. `--feature`) will now be shown as `--feature f1 --feature f2` instead of as `--feature ['f1', 'f2']`.
* Fix: `date` and `time` is no longer shown as the submit command automatically adds these.

open-error / open-output:
* Fix: Could not open logs from job that was split into multiple subjobs due to walltime being greater than split time.

resubmit:
* Fix: Adding `--confirm` or `--no-confirm` will now override the option from the resubmitted job. 

## v1.4.0

New commands:
* open-error: Show the error log of a given job ID in your default text editor.
* open-output: Show the output log of a given job ID in your default text editor.

History:
* Display submission date and time

Submit:
* `--confirm / --no-confirm`: Show and confirm job script before submitting. Default to true.

Resubmit:
* `--confirm / --no-confirm`: Show and confirm job script before resubmitting. Default to true.

Bug fixes:
* resubmit: `sync` would always be true regardless of the value in the history.

## v1.3.1

Bug fixes:
* general: upgraded typer to 0.15.4 to [fix incompatibility with click 8.2.0](https://github.com/fastapi/typer/discussions/1215)
* submit: active branch would not get inserted when "submit" was missing in the config

## v1.3.0

New commands:
* get-options: Similar to get-command, but only retrieves the selected options instead of the full command.

Config:
* Option to specify modules that will automatically be loaded when using `install` and `submit`.
* Profiles: Use `--profile` option to choose a profile from the config. Profiles make it easy to define specific configurations for different types of jobs.

Submit:
* Sync is now run after a job script has been confirmed.

## v1.2.0

Option to show CLI version with `--version`.

Install:
* Run install commands on the active branch.

Remove:
* Show default option in prompt when using `--from-history`.

Run:
* Run a single command instead of potentially multiple.
* All arguments are passed on to the remote command. E.g. `dtu run "ls -a"` is now `dtu run ls -a`.

Submit:
* Branch defaults to the active branch.

Sync:
* Delete files remotely if they have been removed locally.
* Automatically sync when running install, submit, and resubmit (option to opt-out in config).
* Warn about uncommitted changes before synchronizing.

## v1.1.0

New commands:
* get-command
* queues
* run
* start-time
* stats

History:
* History list is no longer reversed, such that newest entries appear at the bottom.
* Added options to filter the history.
* Limit defaults to 5.

List:
* Renamed to *jobs* to better comply with the other *list* commands (*history* and *queues*).

Remove:
* Added `--from-history` option. This will search the history and add any extra job IDs associated with the submissions of a job (due to splitting).

Bug fixes and enhancements:
* SSH connections would only allow for a maximum duration of 30 seconds for a command to finish.
* `--feature`, `--model` and `--queue` will now accept any string value. Was previously restricted to known enumerations, but we removed this because we cannot know these at all times.
* All commands have short descriptions (enter `dtu --help` to see them).