from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from gas.core.config import config, CONFIG_PATHS

console = Console()


@click.group()
def config_cmd():
    """Manage gas configuration."""
    pass


@config_cmd.command()
@click.argument("key")
@click.argument("value")
@click.option(
    "--scope",
    type=click.Choice(["local", "global"]),
    default="local",
    help="Where to save the setting (local or global)",
)
def set(key: str, value: str, scope: str):
    """Set a configuration value.

    Examples:
        gas config set ai.model "your-model-name"
        gas config set user.language "es" --scope global
    """
    try:
        # Convert string value to appropriate type based on current value
        current_value = config.get_value(key)
        if isinstance(current_value, bool):
            value = value.lower() in ("true", "1", "yes", "on")
        elif isinstance(current_value, int):
            value = int(value)
        elif isinstance(current_value, float):
            value = float(value)

        # Set the new value
        config.set_value(key, value, scope)
        console.print(f"[green]✓ Set {key} = {value} in {scope} config[/green]")

    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return 1


@config_cmd.command()
@click.argument("key", required=False)
def get(key: Optional[str]):
    """Get a configuration value.

    If no key is provided, shows all configuration values.

    Examples:
        gas config get
        gas config get ai.model
    """
    try:
        if key:
            value = config.get_value(key)
            console.print(f"{key} = {value}")
        else:
            # Show all config values in a table
            table = Table(title="Current Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Source", style="yellow")

            # Get values from both scopes
            global_config = config._load_file(CONFIG_PATHS["global"]) or {}
            local_config = config._load_file(CONFIG_PATHS["local"]) or {}

            for option in config.list_options():
                path = option["path"]
                value = config.get_value(path)

                # Determine source
                in_local = _get_nested_value(local_config, path.split(".")) is not None
                in_global = _get_nested_value(global_config, path.split(".")) is not None

                if in_local:
                    source = "local"
                elif in_global:
                    source = "global"
                else:
                    source = "default"

                table.add_row(path, str(value), source)

            console.print(table)

    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return 1


@config_cmd.command()
def list():
    """List all available configuration options."""
    table = Table(title="Available Configuration Options")
    table.add_column("Setting", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Default", style="yellow")

    for option in config.list_options():
        table.add_row(option["path"], option["description"], option["default"])

    console.print(table)


def _get_nested_value(d: dict, keys: list) -> Optional[str]:
    """Get a nested dictionary value using a list of keys."""
    for key in keys:
        if not isinstance(d, dict) or key not in d:
            return None
        d = d[key]
    return d
