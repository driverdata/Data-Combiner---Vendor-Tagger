#!/usr/bin/env python3
"""tools/dev_tools.py

Small developer CLI for common tasks:
- check-deps
- format (black + isort)
- lint (ruff)
- test (pytest)
- install-venv (create a venv)

Usage:
    python tools/dev_tools.py format
    python tools/dev_tools.py lint
    python tools/dev_tools.py test
    python tools/dev_tools.py check-deps
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, check=True):
    print("Running:", " ".join(cmd))
    return subprocess.run(cmd, cwd=str(ROOT), check=check)


def cmd_format(args):
    run([sys.executable, "-m", "black", "--line-length", "88", "--quiet", "."])
    run([sys.executable, "-m", "isort", "."])


def cmd_lint(args):
    run([sys.executable, "-m", "ruff", "check", "."])


def cmd_test(args):
    run([sys.executable, "-m", "pytest", "-q"])


def cmd_check_deps(args):
    run([sys.executable, "tools/check_deps.py", "--requirements", "requirements.txt"])


def cmd_install_venv(args):
    venv_dir = ROOT / ".venv"
    if venv_dir.exists():
        print(f"Virtualenv already exists at {venv_dir}")
        return
    run([sys.executable, "-m", "venv", str(venv_dir)])
    print("Created virtualenv at .venv")


def main(argv=None):
    p = argparse.ArgumentParser(prog="dev_tools")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("format")
    sub.add_parser("lint")
    sub.add_parser("test")
    sub.add_parser("check-deps")
    sub.add_parser("install-venv")
    args = p.parse_args(argv)

    if args.cmd == "format":
        cmd_format(args)
    elif args.cmd == "lint":
        cmd_lint(args)
    elif args.cmd == "test":
        cmd_test(args)
    elif args.cmd == "check-deps":
        cmd_check_deps(args)
    elif args.cmd == "install-venv":
        cmd_install_venv(args)
    else:
        p.print_help()


if __name__ == "__main__":
    raise SystemExit(main())
