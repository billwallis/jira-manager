from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from collections.abc import Sequence
from typing import assert_never

from jira_manager import client, create


def _get_version() -> str:
    return f"%(prog)s {importlib.metadata.version('jira-manager')}"


def _get(args: argparse.Namespace) -> int:
    if args.domain == "issue":
        jc = client.JiraClient(
            domain=os.environ["JIRA_DOMAIN"],
            key=os.environ["JIRA_KEY"],
            secret=os.environ["JIRA_SECRET"],
        )
        print(json.dumps(jc.get_issue(args.issue_id_or_key)))
        return 0

    raise assert_never(args.domain)  # this should be handled by argparse


def _create(args: argparse.Namespace) -> int:
    if args.domain == "issue":
        jc = client.JiraClient(
            domain=os.environ["JIRA_DOMAIN"],
            key=os.environ["JIRA_KEY"],
            secret=os.environ["JIRA_SECRET"],
        )
        # TODO: Get the properties interactively, like the copier `copy` command
        create_payload = create.CreatePayload(
            summary="this is a test",
        )
        try:
            response = jc.create_issue(payload=create_payload.to_payload())
            key = response["key"]
            url = jc.base_url + f"browse/{key}"
            print(json.dumps({"key": key, "url": url}))
            return 0
        except RuntimeError as err:
            print(err)
            return 1

    raise assert_never(args.domain)  # this should be handled by argparse


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

    parser__get = subparsers.add_parser("get")
    get__subparsers = parser__get.add_subparsers(dest="domain")
    get__subparsers__issue = get__subparsers.add_parser("issue")
    get__subparsers__issue.add_argument("issue_id_or_key")

    parser__create = subparsers.add_parser("create")
    create__subparsers = parser__create.add_subparsers(dest="domain")
    create__subparsers.add_parser("issue")

    args = parser.parse_args(argv)
    if args.command == "get":
        return _get(args)
    if args.command == "create":
        return _create(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
