---
name: uv-profiles
description: >
  Run and manage named uv Python environments ("uv profiles") under WORKON_HOME.
  Use when running Python, executing a Python file/script, REPL, python --version,
  pip/uv pip install, or venv/virtualenv - prefer uv profiles (uv profiles/uv runenv/uv activate) when profiles exist.
---

# uv-profiles

Reusable named Python environments managed by the `uv` wrapper from uv-profiles
(bash on Linux/WSL, PowerShell on Windows) under `WORKON_HOME` (default
`~/.virtualenvs`).

Profile layout: `$WORKON_HOME/<name>/bin/python` (POSIX) or
`$WORKON_HOME/<name>/Scripts/python.exe` (Windows). A profile is "valid" when
both the python binary and the activation marker (`bin/activate` /
`Activate.ps1`) exist; the marker is only a validity check, never sourced.

## Core commands

| Command | What it does |
| --- | --- |
| `uv profiles` | List profiles: `NAME`, `PYTHON`, `STATUS` (active/inactive) |
| `uv venv <name> --python 3.12` | Create a profile under `WORKON_HOME` |
| `uv activate <name>` | Activate a profile in the current shell |
| `deactivate` | Revert the current shell to its pre-activation state |
| `uv runenv <name> <script> [args...]` | Run a script with the profile's Python without touching the shell |
| anything else | Passed through to the real `uv` unchanged |

## Workflows

### Run a Python file (no shell changes)

```bash
uv runenv data run.py          # run with the 'data' profile's Python
uv runenv data report.py --arg value
uv runenv data gen.py > out.txt   # capture output
echo $?                        # script exit code is propagated
```

```powershell
uv runenv data .\run.py --arg value
```

Script path must exist and the profile must have a usable python executable.
No activation required.

### Interactive Python session in a profile

```bash
uv activate data
python --version               # now the profile's Python
python                        # REPL / interactive session
uv pip install requests       # installs into the active profile
deactivate                    # restore shell
```

```powershell
uv activate data
python ...                     # REPL / scripts
deactivate
```

Re-activating the currently active profile is a no-op. `uv activate` refuses
to run while an external `VIRTUAL_ENV` is in scope.

### Create a new profile

```bash
uv venv data --python 3.12     # 3.11, 3.13, etc. all valid
uv profiles                    # confirm it appears
```

`uv venv` manages bare plain names under `WORKON_HOME`; path-like, absolute,
and option-first targets pass through to `uv` unchanged.

### When the `uv` wrapper is not loaded

If the runtime isn't loaded (bash `type uv` isn't a function; PowerShell
`Get-Command uv` doesn't show the wrapper), load it:

```bash
source "$HOME/.local/share/uv/uv-profile.sh"   # installed bash runtime
source ./src/uv-profile.sh                     # from the uv-profiles repo
```

```powershell
. "$env:LOCALAPPDATA\uv\uv-profile.ps1"        # installed PS runtime
```

## Pitfalls

- `uv runenv` never mutates the shell. Use it for one-off script runs as `uv runenv <name> <script.py> [args...]` - script path must exist (`uv-profile.ps1:109-110`), not `uv runenv <name> -- python ...`. For ad-hoc commands use `& "$HOME\.virtualenvs\<name>\Scripts\python.exe" --version` / `-c` or `uv activate`.
  `WORKON_HOME` overrides the storage root.
- Standard `uv` commands (e.g. `uv pip install`) need an active profile or an
  explicit python path; bare `python` outside `uv activate` uses PATH.