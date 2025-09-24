"""
Script for creating a pull request from the command line in azure devops.

Install the azure cli: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest
"""

import argparse
import pathlib
import subprocess
import re
import enum
from typing import Optional
from toolit import tool

PATH_DEFAULT_PR_TEMPLATE = pathlib.Path(__file__).parent / "pull_request_template.md"
PATH_DEFAULT_PR_TEMPLATE_HOTFIX = pathlib.Path(__file__).parent / "bugfix_or_hotfix.md"

class PrTemplate(enum.Enum):
    """The different pull request templates supported."""

    DEFAULT = 1
    HOTFIX = 2


def _load_pull_request_template(pr_template: PrTemplate) -> str:
    """Load the pull request template."""
    if pr_template == PrTemplate.DEFAULT:
        template_path = PATH_DEFAULT_PR_TEMPLATE
    elif pr_template == PrTemplate.HOTFIX:
        template_path = PATH_DEFAULT_PR_TEMPLATE_HOTFIX
    with open(template_path) as fp:
        return fp.read()


def _get_branch_name() -> str:
    """Get git branch name."""
    sp_args: list[str] = [
        "git",
        "rev-parse",
        "--abbrev-ref",
        "HEAD",
    ]
    result = subprocess.run(sp_args, capture_output=True)
    return result.stdout.decode("utf-8").strip()


def _get_work_item_id_from_branch_name(branch_name: str) -> Optional[str]:
    """Get the work item id from the branch name indicated with a "wi" followed by a number."""
    match = re.search(r"wi(\d+)", branch_name)
    if match:
        return match.group(1)
    else:
        return None


@tool
def create_pull_request(title: str, description: str, draft: bool):
    """Create pull reqeust using the az cli."""
    branch = _get_branch_name()
    pr_template_to_use = PrTemplate.DEFAULT

    secondary_target_branch: Optional[str] = None
    if branch.startswith("hotfix/"):
        matches = re.match(r"hotfix\/(?P<target_branch>.*)\/(.+)", branch)
        secondary_target_branch = matches.group("target_branch")
        print(f"A hotfix branch was detected, will create an additional PR to: {secondary_target_branch}")
        pr_template_to_use = PrTemplate.HOTFIX
        if not secondary_target_branch:
            raise Exception(f"Could not find source branch from branch name: {branch}")

    if branch.startswith("bugfix/"):
        pr_template_to_use = PrTemplate.HOTFIX

    work_item = _get_work_item_id_from_branch_name(branch)
    pull_request_template = _load_pull_request_template(pr_template_to_use)
    # C:\\Program Files (x86)\\Microsoft SDKs\\Azure\\CLI2\\wbin\\az.cmd
    sp_args: list[str] = [
        "az.cmd",
        "repos",
        "pr",
        "create",
        "--open",
        "--delete-source-branch",
        "--draft",
        "true" if draft else "false",
        "--title",
        f"{title}",
    ]
    if work_item:
        sp_args.append("--work-items")
        sp_args.append(f"{work_item}")
    sp_args.append("--description")
    sp_args.extend(f"{description}\n\n{pull_request_template}".splitlines())
    print("Running command:")
    print(" ".join(sp_args))
    subprocess.run(sp_args)

    if secondary_target_branch:
        print("Creating PR to release branch")
        sp_args.append("--target-branch")
        sp_args.append(secondary_target_branch)
        print("Running command:")
        print(" ".join(sp_args))
        subprocess.run(sp_args)
    print("Finised")


if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description="Create a pull request in azure devops.")
    parser.add_argument("--title", type=str, help="Title of the pull request.", default="test")
    parser.add_argument("--description", type=str, help="Description of the pull request.", default="test")
    parser.add_argument("--type", type=str, help="Type of PR created.", default=False)
    args = parser.parse_args()

    if args.type == "Create draft PR":
        print("Configure for creating draft PR")
        draft = True
    else:
        print("Configure for creating published PR")
        draft = False

    # Create pull request
    create_pull_request(args.title, args.description, draft)
