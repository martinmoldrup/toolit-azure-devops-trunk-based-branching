import subprocess
from toolit import tool


@tool
def create_new_task_in_devops(title: str, description: str, work_item_id: str, target_branch: str, draft: bool = False):
    """Create a new task in Azure DevOps."""
    sp_args = [
        "az",
        "boards",
        "work-item",
        "create",
        "--title",
        title,
        "--description",
        description,
        "--type",
        "Task",
        "--id",
        work_item_id,
        "--target-branch",
        target_branch,
        "--draft" if draft else "",
    ]

    result = subprocess.run(sp_args, capture_output=True)

    if result.returncode != 0:
        raise RuntimeError(f"Failed to create task: {result.stderr.decode('utf-8')}")

    print(f"Task created successfully: {result.stdout.decode('utf-8')}")
