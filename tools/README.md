# Tools

This folder contains small developer utilities for the project.

## `check_deps.py`

Usage:

```bash
python tools/check_deps.py --requirements requirements.txt
python tools/check_deps.py --requirements requirements.txt --upgrade
python tools/check_deps.py --requirements requirements.txt --json
```

Notes:
- `requests` and `packaging` are optional runtime dependencies for this script to query PyPI and compare versions. If missing, the script will still work for local installed version checks but will not query PyPI.
- The `--upgrade` flag runs `python -m pip install -U <package>` and will ask for confirmation unless `--yes` is provided.
