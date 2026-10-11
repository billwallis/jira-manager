from __future__ import annotations

import argparse
import importlib.metadata
from collections.abc import Sequence

SUCCESS = 0
FAILURE = 1


def _get_version() -> str:
    return f"%(prog)s {importlib.metadata.version('jira-manager')}"


def _project(args: argparse.Namespace) -> int:
    print("error: not implemented")
    return FAILURE


def main(argv: Sequence[str] | None = None) -> int:
    """
    Parse the arguments and run the command.
    """

    parser = argparse.ArgumentParser(prog="jira-manager")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=_get_version(),
    )
    subparsers = parser.add_subparsers(dest="command")

    parser__repo = subparsers.add_parser("project")
    parser__repo.add_argument("project_key")

    args = parser.parse_args(argv)
    if args.command == "project":
        return _project(args)

    parser.print_help()
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
