# Oxygen CLI

Oxygen replaces the import-and-plot workflow in `bin/fitcli.sh` with Python
commands. It works on Python 3.11+ and does not require shell utilities, a GUI,
or plotting packages for help, validation, dry runs, and imports.

## Installation

Install from the repository root, not from the legacy `oxygen/` setup directory:

```bash
poetry install --with analytics
poetry run oxygen --help
poetry run python -m oxygen --help
```

The root project installs the `oxygen` executable. It also supports
`python -m oxygen`. The legacy setup metadata now declares its dependency on the
Fitness Tracker core; the root project is the supported installation route.

For a smaller install without plots:

```bash
poetry install
poetry run oxygen run --no-figures
```

Plotting loads optional analytics packages only when requested. Missing plotting
dependencies fail before a combined workflow imports records. `--help` does not
require an existing data directory. `--version` reports the installed core version.

Editable project installs use the repository configuration and root `.env`, even
when invoked from another directory. Wheel installs include the static settings
and training metadata, but not personal archives, `.env`, or credentials; supply
your data path explicitly with environment variables or `--data-dir`.

## Source logs

Input files use the same directory layout as the shell workflow:

```text
DATA_DIR/
  log_archive/
    YML/2024/March/
      athlete_training_log_2024-03-11.yml
      athlete_training_log_2024-03-11_2.yml
      athlete_training_log_2024-03-11_10.yml
    JSON/2024/March/
      athlete_training_log_2024-03-18.json
```

Use lowercase `.yml` or `.json` extensions and English month directories. Prefixes
before `training_log_` are allowed. Logs may be in nested directories under the
month folder. Numbered files are ordered numerically, so `_2` precedes `_10`.
Unnumbered files and `_1` are treated as workout number one when using `-w 1`.
Symlinks must not escape the selected archive directory.

A minimal YAML workout is:

```yaml
date: "2024-03-11"
split: push
start_time: "09:00"
end_time: "10:00"
notes: Morning training
exercises:
  bb_bench_press:
    - set_number: 1
      reps: 5
      weight: "60 kg"
```

The record date must match the filename's selected date. The existing workout
model validates dates and set structure. Optional metadata and supplied UUIDs are
preserved. Use canonical exercise identifiers; control characters, path separators,
and Windows-unsafe filename punctuation are rejected before import or plotting.

## Commands

The combined workflow imports records and prepares figures, without opening a GUI:

```bash
poetry run oxygen run -d 2024-03-11 --dry-run
poetry run oxygen run -d 2024-03-11,2024-03-18 --no-open
poetry run oxygen run -d 2024-03-11 -d 2025-01-02 --open
```

Repeat `-d` or use comma-separated dates. Repeated dates are processed once.
Dates must be real ISO calendar dates between 1900 and 2100. With no date option,
the selected date is today's local date, calculated for each invocation.

Use individual steps when appropriate:

```bash
poetry run oxygen insert -d 2024-03-11 -f yml
poetry run oxygen insert -d 2024-03-18 -f json -w 2
poetry run oxygen run -d 2024-03-18 -f json --no-figures
poetry run oxygen prepare-figures -y 2024 -m March
poetry run oxygen open-images -y 2024 -m 03
poetry run oxygen show-help
```

`--workout-date`, `--dates`, and `-d` are aliases. `--file-format` accepts `yml` and
`json` case-insensitively. `--workout-number`/`-w` selects one positive numbered
workout; otherwise every matching log is imported. Month options accept full
names, three-letter abbreviations, and numbers 1-12. Years and months default to
the current local period. Legacy underscored command names such as
`prepare_figures`, `open_images`, and `show_help` remain accepted.

`run --dry-run` validates inputs and conflicts and prints proposed changes and
plot periods without writing archives, images, or SQLite. It does not require
analytics packages. `--no-figures` skips plotting entirely; combining it with
`--open` is a usage error.

## Paths and configuration

Global options go before the command:

```bash
poetry run oxygen --data-dir "/path/with spaces/workouts" \
  --image-dir "/path/with spaces/reports" run -d 2024-03-11 --dry-run
poetry run oxygen --config ./oxygen.toml insert -d 2024-03-11
```

An Oxygen configuration file is TOML, not a shell script:

```toml
[oxygen]
data_dir = "workouts"
image_dir = "reports"
```

The same keys may appear at the top level instead of `[oxygen]`. Only string
`data_dir` and `image_dir` values are accepted. Relative paths in TOML are resolved
relative to the configuration file; explicit command-line paths are relative to
the working directory. Command-line options override TOML, which overrides the
project settings. Shell configurations are never sourced or executed.

`--data-dir` selects both raw logs and `<YEAR>_workouts.yml` targets, and defaults
image output to its `img/` directory unless another image path is supplied.
Without that override, `FITNESS_TRACKER_DATA_DIR`, `FITNESS_TRACKER_IMG_PATH`, and
custom project database templates remain respected. Paths are joined safely and
do not need trailing slashes.

SQLite selection continues to use `FITNESS_TRACKER_STATE_DIR`, or
`DATA_DIR/.state` when unset. If a state directory is explicitly configured, it
is not changed by `--data-dir`; select the correct athlete's state before plotting.

## Imports and repeated runs

Oxygen validates every selected source and all ID conflicts before writing any
target records. Each date routes to its own year, including batches crossing year
boundaries. Source logs are not modified. Writes use the existing atomic YAML
storage, with one batch write per year.

An input without an ID receives a stable UUID derived from its relative archive
filename, not its date or changing contents. A supplied ID is preserved. Repeating
an unchanged import skips the existing record without rewriting the archive.
Separate same-day files receive distinct identities, even if their contents match.
Changing an already-imported file produces an ID conflict instead of overwriting
history; edit the workout in the app or use a new file for an intentional new session.

Renaming a file without a supplied ID changes its identity. Imports previously
created by another tool are not guessed from matching dates or contents: preserve
the original stored UUID in the raw log when adopting those records. Existing
legacy UUID fallback identities remain supported without write-on-read migration.

This is a trusted, local filesystem workflow. It writes YAML archives directly,
not API-created SQLite workouts, and does not bypass filesystem permissions.
Keep a single YAML writer and avoid simultaneous CLI/app edits to imported records.
Back up YAML and SQLite together before maintenance.

Validation errors write no target records. A later filesystem failure can leave
earlier years committed; there is no cross-file transaction. Plotting or image
opening can also fail after imports have committed. Failures return nonzero and
do not print a successful completion summary. Retrying unchanged inputs is safe.

## Figures and desktop opening

Figures merge imported YAML with local SQLite additions, edits, and deletion
markers. Generation uses the existing frequency, duration/volume, and estimated
1RM implementations with a non-interactive Matplotlib backend. `run` prepares each
distinct selected year/month once.

```text
IMG_PATH/2024/
  2024_workout_frequency.png
  workout_duration_March_2024.png
  workout_duration_volume_1rm_bb_bench_press.png
```

The last figure's exercise depends on available data. Oxygen puts that year-scoped
figure beside the other outputs rather than overwriting another year's `all_years`
image. Some metrics cannot be plotted without sufficient timed or known-load data.
Only generated files are reported; a run producing no figures fails clearly.

Plots are staged before publication. Each PNG is replaced atomically, so render or
copy failures do not corrupt an existing image. PNG publication is per file, not
one transaction for the entire set. Output symlinks cannot escape the configured
image directory.

Use `--open` or `open-images` to opt into a desktop viewer. Oxygen uses `open` on
macOS, `xdg-open` on Linux, and `os.startfile` on Windows, without a shell. Missing
viewers or files fail clearly. On servers, leave opening disabled and use the
printed paths. Oxygen itself creates no extra growing log files.

## Verification

```bash
poetry run pytest test/test_oxygen.py
poetry run ruff check --config .config/ruff.toml src oxygen test
poetry run mypy --config-file .config/mypy.ini src oxygen/oxygen
```

Tests cover temporary real YAML/JSON imports, multi-year and same-day routing,
stable reimports and legacy IDs, invalid input and symlink boundaries, safe TOML
configuration, runtime date defaults, headless operation, optional dependencies,
SQLite-aware plots, real PNG generation, and mocked macOS/Linux/Windows viewers.
The real renderer test requires the optional analytics group. No test opens a
desktop viewer or writes to personal archives.
