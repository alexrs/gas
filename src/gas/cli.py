import sys

import click
from rich.console import Console

from gas.commands.config import config_cmd
from gas.commands.commit import generate_commit_message
from gas.core.git import get_git_diff

console = Console()


@click.group()
@click.version_option()
def cli():
    """Git AI Sidekick - Your intelligent Git assistant."""
    pass


@cli.command()
@click.option("--detailed", "-d", default=False, help="Show detailed explanation")
def explain(detailed):
    """Explain Git diff changes in plain English.

    By default, explains the current working directory changes.
    Can also read from stdin if piped:
    $ git diff | gas explain
    """
    from gas.commands.explain import explain_diff

    # Check if we're receiving input from a pipe
    if not sys.stdin.isatty():
        diff_content = sys.stdin.read()
    else:
        # No pipe, use get_git_diff
        diff_content = get_git_diff()

    explain_diff(diff_content, detailed=detailed)


@cli.command()
@click.option(
    "--type",
    "-t",
    type=click.Choice(["feat", "fix", "docs", "style", "refactor", "test", "chore"]),
    help="Type of change (conventional commits)",
)
@click.option("--edit/--no-edit", default=True, help="Open editor before committing")
def commit(type, edit):
    """Generate a commit message based on staged changes."""
    generate_commit_message(commit_type=type, edit=edit)


# Add the config command group
cli.add_command(config_cmd, name="config")

if __name__ == "__main__":
    cli()
