import subprocess
from typing import Optional

import click
from rich.console import Console
from rich.prompt import Confirm
from rich.status import Status

from gas.core.ai import get_ai_client
from gas.core.git import get_staged_changes
from gas.core.config import config

console = Console()

def generate_commit_message(commit_type: Optional[str] = None, edit: bool = True) -> None:
    """Generate a commit message based on staged changes.

    Args:
        commit_type: Type of change (conventional commits)
        edit: Whether to open editor before committing
    """
    # Get staged changes
    with Status("[bold blue]📝 Reading staged changes...", spinner="dots") as status:
        staged_changes = get_staged_changes()

        if not staged_changes:
            status.update("[yellow]⚠️ No changes found")
            console.print("[yellow]No staged changes found. Stage some changes first.[/yellow]")
            return

    try:
        # Generate commit message
        message = _generate_message(staged_changes, commit_type)

        # Show the message and confirm
        console.print("\n[bold green]✨ Generated commit message:[/bold green]")
        console.print(message)

        if edit:
            with Status("[bold blue]📝 Opening editor...", spinner="dots"):
                # Save message to temporary file and open editor
                message = _edit_message(message)

        if Confirm.ask("\n[bold]Do you want to commit with this message?[/bold]"):
            with Status("[bold blue]📝 Committing changes...", spinner="dots") as status:
                _commit_changes(message)
                status.update("[bold green]✅ Changes committed successfully!")

    except Exception as e:
        console.print(f"[red]❌ Error generating commit message: {str(e)}[/red]")

def _generate_message(changes: str, commit_type: Optional[str]) -> str:
    """Generate a commit message using AI."""
    prompt = _build_commit_prompt(changes, commit_type, language=config.user.language)

    client = get_ai_client()
    response = client.generate(
        prompt=prompt,
        max_tokens=config.ai.max_tokens,
        temperature=config.ai.temperature,
    )

    return response.strip()

def _build_commit_prompt(changes: str, language: str = "en", commit_type: Optional[str] = None) -> str:
    """Build the prompt for commit message generation."""
    language_prompt = "" if language == "en" else f"Please respond in {language} language.\n\n"

    base_prompt = f"""{language_prompt}You are an expert at writing Git commit messages.
    Please generate a clear and concise commit message for the following changes.
    Follow these guidelines:
    - Use the imperative mood ("Add feature" not "Added feature")
    - First line should be a short summary (50 chars or less)
    - If needed, add a detailed description after a blank line
    - Reference any relevant issue numbers if found in the diff
    - Be specific about what changed and why
    - Focus on the intention of the change, not just what files changed
    """

    if commit_type:
        base_prompt += f"""
        Use the conventional commit format with type '{commit_type}' and follow these rules:
        - Format: {commit_type}([scope]): description
        - A scope MAY be provided after a type. A scope MUST consist of a noun describing a section of the codebase surrounded by parenthesis, e.g., fix(parser):
        - Description should clearly state the purpose
        - Add a body if more context is needed
        - Add breaking change warnings if applicable
        """

    return f"{base_prompt}\n\nChanges:\n{changes}"

def _edit_message(message: str) -> str:
    """Open the default editor to edit the commit message."""
    with click.edit(message) as edited:
        return edited if edited is not None else message

def _commit_changes(message: str) -> None:
    """Commit the changes with the given message."""
    subprocess.run(['git', 'commit', '-m', message], check=True)
