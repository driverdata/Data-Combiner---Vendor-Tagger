#!/usr/bin/env python3
"""tools/check_deps.py

Simple dependency checker for a project's `requirements.txt`.

Features:
- Reads a requirements file and lists packages
- Checks installed vs latest PyPI versions
- Reports missing / up-to-date / outdated packages
- Optional `--upgrade` to run `pip install -U` for selected packages (with confirmation)
- Can output JSON for programmatic use

Usage:
    python tools/check_deps.py --requirements requirements.txt
    python tools/check_deps.py --requirements requirements.txt --upgrade --yes

"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple

try:
    # Python 3.8+: importlib.metadata available in stdlib
    from importlib.metadata import version as installed_version
except Exception:  # pragma: no cover - fallback
    def installed_version(pkg_name: str) -> str:  # type: ignore
        raise ImportError("importlib.metadata not available in this Python")

try:
    import requests
except ImportError:  # pragma: no cover - keep dependency optional
    requests = None

try:
    from packaging.version import parse as parse_version
    from packaging.requirements import Requirement
except Exception:  # pragma: no cover - soft fallback
    parse_version = None  # type: ignore
    Requirement = None  # type: ignore

PYPI_URL = "https://pypi.org/pypi/{name}/json"


@dataclass
class DepStatus:
    name: str
    spec: str
    installed: Optional[str]
    latest: Optional[str]
    status: str  # missing|up-to-date|outdated|error


def read_requirements(path: str) -> List[str]:
    lines: List[str] = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            # Skip editable / VCS requirements
            if line.startswith("-e") or "git+" in line or line.startswith("https://"):
                continue
            lines.append(line)
    return lines


def req_name_and_spec(req_line: str) -> Tuple[str, str]:
    # Try packaging.Requirement when available to handle extras and markers
    if Requirement is not None:
        try:
            r = Requirement(req_line)
            return r.name, req_line
        except Exception:
            pass
    # Fallback: split on common version operators
    m = re.split(r"\s*(==|>=|<=|~=|>|<)\s*", req_line, maxsplit=1)
    if len(m) >= 3:
        name = m[0]
        return name, req_line
    # fallback plain
    name = re.split(r"[=<>!~]", req_line, maxsplit=1)[0]
    return name, req_line


def get_latest_version_from_pypi(name: str) -> Optional[str]:
    if requests is None:
        raise RuntimeError("requests library is required to query PyPI. Install it to enable this feature.")
    try:
        r = requests.get(PYPI_URL.format(name=name), timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        return data.get("info", {}).get("version")
    except Exception:
        return None


def check_deps(requirements_path: str) -> List[DepStatus]:
    specs = read_requirements(requirements_path)
    results: List[DepStatus] = []
    for spec in specs:
        name, _ = req_name_and_spec(spec)
        try:
            try:
                inst = installed_version(name)
            except Exception:
                inst = None
            latest = None
            try:
                latest = get_latest_version_from_pypi(name)
            except Exception:
                latest = None

            if not inst:
                status = "missing"
            elif latest and parse_version is not None:
                try:
                    if parse_version(inst) < parse_version(latest):
                        status = "outdated"
                    else:
                        status = "up-to-date"
                except Exception:
                    status = "error"
            else:
                status = "unknown"

            results.append(DepStatus(name=name, spec=spec, installed=inst, latest=latest, status=status))
        except Exception as e:  # pragma: no cover - defensive
            results.append(DepStatus(name=name, spec=spec, installed=None, latest=None, status=f"error: {e}"))
    return results


def print_table(results: List[DepStatus]) -> None:
    # Compute column widths
    cols = ["package", "spec", "installed", "latest", "status"]
    rows = []
    for r in results:
        rows.append([r.name, r.spec, r.installed or "-", r.latest or "-", r.status])
    widths = [max(len(str(cell)) for cell in col) for col in zip(*([cols] + rows))]
    fmt = "  ".join(f"{{:{w}}}" for w in widths)
    print(fmt.format(*cols))
    print("-" * (sum(widths) + 2 * (len(widths) - 1)))
    for row in rows:
        print(fmt.format(*row))


def upgrade_packages(pkgs: List[DepStatus], assume_yes: bool = False) -> None:
    to_install = [p.name for p in pkgs if p.status in ("missing", "outdated")]
    if not to_install:
        print("No packages to upgrade/install.")
        return
    print("Packages to install/upgrade:")
    for p in to_install:
        print(f" - {p}")
    if not assume_yes:
        yn = input("Proceed with pip install -U for the above packages? [y/N]: ").strip().lower()
        if yn not in ("y", "yes"):
            print("Aborted by user.")
            return
    for pkg in to_install:
        cmd = [sys.executable, "-m", "pip", "install", "-U", pkg]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)
    print("Upgrade complete.")


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Check installed packages against PyPI for a requirements file.")
    p.add_argument("--requirements", "-r", default="requirements.txt", help="Path to requirements file")
    p.add_argument("--json", action="store_true", help="Output results as JSON")
    p.add_argument("--upgrade", action="store_true", help="Offer to upgrade missing/outdated packages")
    p.add_argument("--yes", action="store_true", help="Assume yes for upgrades (no confirmation)")
    args = p.parse_args(argv)

    try:
        results = check_deps(args.requirements)
    except Exception as exc:
        print("Error while checking dependencies:", exc)
        return 2

    if args.json:
        out = [r.__dict__ for r in results]
        print(json.dumps(out, indent=2))
    else:
        print_table(results)

    if args.upgrade:
        try:
            upgrade_packages(results, assume_yes=args.yes)
        except subprocess.CalledProcessError as e:
            print("An error occurred while running pip:", e)
            return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
