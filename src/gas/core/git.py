import subprocess
from typing import Optional


def parse_git_diff(diff_content: str) -> str:
    """Parse the git diff content into a structured format.

    Args:
        diff_content: Raw git diff content

    Returns:
        Structured representation of the changes
    """
    # For now, we'll return the raw diff content
    # In the future, we can parse this into a more structured format
    return diff_content.strip()


def get_staged_changes() -> Optional[str]:
    """Get the staged changes in the repository.

    Returns:
        String containing the staged changes or None if no changes
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_current_branch() -> str:
    """Get the name of the current branch."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def is_git_repository() -> bool:
    """Check if the current directory is a git repository."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_git_diff() -> str:
    """Get the git diff for the current branch."""
    return subprocess.check_output(["git", "diff"]).decode("utf-8")
