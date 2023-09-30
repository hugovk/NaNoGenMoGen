"""
Tool to help create NaNoGenMo each year.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import subprocess
import textwrap
from functools import cache
from pathlib import Path


@cache
def this_year() -> int:
    """Return this year."""
    return dt.datetime.now().year


@cache
def last_year() -> int:
    """Return last year."""
    return this_year() - 1


def run_commands(commands: str) -> None:
    """Run commands."""
    for command in textwrap.dedent(commands).splitlines():
        if command:
            print(command)
            subprocess.run(command, shell=True, check=True)


def create_repo() -> None:
    """Create a repo for this year."""
    # https://stackoverflow.com/a/16762475/724176
    repo = f"hugovk/{this_year()}"
    print(f"Creating https://github.com/{repo}...")
    print()

    # Move to a scratch dir
    Path("/tmp/create-repo").mkdir(parents=True, exist_ok=True)
    os.chdir("/tmp/create-repo")

    commands = f"""\
    # Create destination repo on GitHub
    gh repo create {this_year()} --private

    # Make a bare clone of the repository
    git clone --bare https://github.com/NaNoGenMo/{last_year()}.git
    """
    run_commands(commands)

    os.chdir(f"/tmp/create-repo/{last_year()}.git")

    commands = f"""\
    # Mirror-push to the new repository
    git push --mirror https://github.com/hugovk/{this_year()}.git
    """
    run_commands(commands)

    shutil.rmtree("/tmp/create-repo/", ignore_errors=True)

    print(f"Created: https://github.com/{repo}")


def clone_repo() -> None:
    """Clone a repo for this year."""
    # Move to a scratch dir
    Path("/tmp/update-repo").mkdir(parents=True, exist_ok=True)

    run_commands(
        f"git clone https://github.com/hugovk/{this_year()} /tmp/update-repo/{this_year()}"
    )


def update_readme() -> None:
    """Update README for this year."""
    os.chdir(f"/tmp/update-repo/{this_year()}")

    with open("README.md") as f:
        readme = f.read()

    for old, new in (
        (f"# NaNoGenMo {last_year()}", f"# NaNoGenMo {this_year()}"),
        (
            f"NaNoGenMo/{last_year()}/issues?q=label",
            f"NaNoGenMo/{this_year()}/issues?q=label",
        ),
        (f"This is the {last_year()} edition.", f"This is the {this_year()} edition."),
        (
            f"* [{last_year() - 1}](https://github.com/NaNoGenMo/{last_year() - 1})",
            f"* [{last_year()}](https://github.com/NaNoGenMo/{last_year()})\n"
            f"* [{last_year() - 1}](https://github.com/NaNoGenMo/{last_year() - 1})",
        ),
        (
            f"* [{last_year() - 1}](https://github.com/NaNoGenMo/{last_year() - 1}/issues/1)",
            f"* [{last_year() - 1}](https://github.com/NaNoGenMo/{last_year() - 1}/issues/1)\n"
            f"* [{last_year()}](https://github.com/NaNoGenMo/{last_year()}/issues/1)",
        ),
    ):
        readme = readme.replace(old, new)

    print(readme)
    with open("README.md", "w") as f:
        f.write(readme)

    run_commands("git add README.md")
    run_commands(f"git commit -m '{last_year()} -> {this_year()}'")
    run_commands("git push")


def create_labels() -> None:
    os.chdir(f"/tmp/update-repo/{this_year()}")
    run_commands(f"gh label clone NaNoGenMo/{last_year()}")
    run_commands("gh label list")
    for old in (
        "bug",
        "documentation",
        "duplicate",
        "enhancement",
        "good first issue",
        "help wanted",
        "invalid",
        "question",
        "wontfix",
    ):
        run_commands(f'gh label delete --yes "{old}"')
    run_commands("gh label list")
    print(f"https://github.com/hugovk/{this_year()}/labels")


def create_issues() -> None:
    os.chdir(f"/tmp/update-repo/{this_year()}")

    # Create issue 1 text
    text = textwrap.dedent(
        """\
    This is an open issue where you can comment and add resources that might come in handy for NaNoGenMo.

    There are already a ton of resources on the old resources threads of previous editions:

    """
    )
    for year in range(last_year(), 2016 - 1, -1):
        text += f"* [{year}](https://github.com/NaNoGenMo/{year}/issues/1)\n"

    text += "* [2015](https://github.com/dariusk/NaNoGenMo-2015/issues/1)\n"
    text += "* [2014](https://github.com/dariusk/nanogenmo-2014/issues/1)\n"
    text += "* [2013](https://github.com/dariusk/NaNoGenMo/issues/11)\n"
    with open("/tmp/issue1.txt", "w") as f:
        f.write(text)

    # Create issue 2 text
    text = "Links to previous years:\n\n"
    for year in range(last_year(), 2016 - 1, -1):
        text += f"* [{year}](https://github.com/NaNoGenMo/{year}/issues/2)\n"

    text += "* [2016](https://github.com/NaNoGenMo/2016/issues/5)\n"
    text += "* [2015](https://github.com/dariusk/NaNoGenMo-2015/issues/9)\n"
    text += "* [2014](https://github.com/dariusk/NaNoGenMo-2014/issues/92)\n"

    with open("/tmp/issue2.txt", "w") as f:
        f.write(text)

    # Create issues on GitHub
    run_commands(
        'gh issue create --label "admin" --body-file "/tmp/issue1.txt" --title "Resources"'
    )
    run_commands(
        'gh issue create --label "admin" --body-file "/tmp/issue2.txt" --title "Press and other coverage"'
    )
    run_commands("gh issue list")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Commands for generating a NaNoGenMo repo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--create-repo", action="store_true", help="Create repo")
    parser.add_argument("--clone-repo", action="store_true", help="Clone repo")
    parser.add_argument("--update-readme", action="store_true", help="Update README")
    parser.add_argument("--create-labels", action="store_true", help="Create labels")
    parser.add_argument("--create-issues", action="store_true", help="Create issues")
    args = parser.parse_args()

    if args.create_repo:
        create_repo()

    if args.clone_repo:
        clone_repo()

    if args.update_readme:
        update_readme()

    if args.create_labels:
        create_labels()

    if args.create_issues:
        create_issues()

    # After doing all this:
    # [ ] check other repo settings
    # [ ] transfer to NaNoGenMo org
    # [ ] make public
    # [ ] add redirect to last year's repo
    # [ ] add this year to https://github.com/NaNoGenMo/nanogenmo.github.io/blob/main/index.html


if __name__ == "__main__":
    main()
