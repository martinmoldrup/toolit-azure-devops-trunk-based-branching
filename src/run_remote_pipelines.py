"""Run azure devops CI pipeline on current branch."""

import os
import argparse
from toolit.decorators import tool


@tool
def run_cd_release_on_current_branch(pipeline_id: int):
    """Run azure devops CI pipeline on current branch."""
    print("Running Remote CD pipeline on current branch")
    branch = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
    print(f"Branch: {branch}")
    result = os.system(f"az pipelines run --branch {branch} --id {pipeline_id} --open")
    if result != 0:
        raise Exception("Failed to trigger CD pipeline")
    print("Successfully triggered CD pipeline")


@tool
def run_ci_on_current_branch(pipeline_id: int):
    """Run azure devops CI pipeline on current branch."""
    print("Running CI pipeline on current branch")
    branch = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
    print(f"Branch: {branch}")
    result = os.system(f"az pipelines run --branch {branch} --id {pipeline_id} --open")
    if result != 0:
        raise Exception("Failed to trigger CI pipeline")
    print("Successfully triggered CI pipeline")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run azure devops CI/CD pipeline on current branch")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-command to run")

    ci_parser = subparsers.add_parser("ci", help="Run CI pipeline")
    ci_parser.add_argument("--pipeline_id", type=int, required=True, help="ID of the CI pipeline to run")

    cd_parser = subparsers.add_parser("cd", help="Run CD pipeline")
    cd_parser.add_argument("--pipeline_id", type=int, required=True, help="ID of the CD pipeline to run")

    args = parser.parse_args()

    if args.command == "ci":
        run_ci_on_current_branch(args.pipeline_id)
    elif args.command == "cd":
        run_cd_release_on_current_branch(args.pipeline_id)
