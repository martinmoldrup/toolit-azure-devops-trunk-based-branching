"""Helper to create branch with the correct name."""

import os
import argparse
from toolit import tool


@tool
def create_hotfix_branch(name: str):
    """Create hotfix branch."""
    print("Creating hotfix branch")
    name = name.replace(" ", "-").lower().strip()
    current_branch = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
    if not current_branch.startswith("releases/"):
        raise Exception(
            f"Current branch must be a release branch, but was {current_branch}. Create bugfix branches for other scenarios."
        )
    branch_name = f"hotfix/{current_branch}/{name}"
    print(f"Creating branch with name: {branch_name}")
    # Create branch
    os.system(f"git checkout -b {branch_name}")
    print("Finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create hotfix branch")
    parser.add_argument("--name", type=str, help="Name of the hotfix branch")
    args = parser.parse_args()
    create_hotfix_branch(args.name)
