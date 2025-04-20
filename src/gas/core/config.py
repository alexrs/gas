from pathlib import Path
from typing import Optional, Dict, Any, List

import yaml
from pydantic import BaseModel, Field

# Configuration paths in order of precedence (highest to lowest)
CONFIG_PATHS = {
    "local": Path(".gas.yaml"),  # Local repository config
    "global": Path.home() / ".config" / "gas" / "config.yml",  # Global user config
}


class AIConfig(BaseModel):
    """AI-related configuration."""

    model: str = Field(
        default="CohereLabs/c4ai-command-a-03-2025", description="The model to use for generation"
    )
    temperature: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Temperature for generation (0.0 to 1.0)"
    )
    max_tokens: int = Field(default=500, gt=0, description="Maximum number of tokens to generate")


class UserConfig(BaseModel):
    """User preferences configuration."""

    language: str = Field(default="en", description="Language for explanations (ISO 639-1 code)")
    emoji_enabled: bool = Field(default=True, description="Whether to show emojis in output")


class Config(BaseModel):
    """Main configuration class."""

    ai: AIConfig = Field(default_factory=AIConfig)
    user: UserConfig = Field(default_factory=UserConfig)

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from all sources and merge them.

        The local config takes precedence over the global config.
        """
        config_dict = {}

        # Load global config first (if exists)
        global_config = cls._load_file(CONFIG_PATHS["global"])
        if global_config:
            config_dict.update(global_config)

        # Load local config and override global settings
        local_config = cls._load_file(CONFIG_PATHS["local"])
        if local_config:
            config_dict.update(local_config)

        return cls.model_validate(config_dict or {})

    @staticmethod
    def _load_file(path: Path) -> Optional[Dict[str, Any]]:
        """Load a single configuration file."""
        if path.exists():
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        return None

    def save(self, scope: str = "local") -> None:
        """Save configuration to file.

        Args:
            scope: Where to save the config ('local' or 'global')
        """
        if scope not in CONFIG_PATHS:
            raise ValueError(
                f"Invalid scope: {scope}. Must be one of: {', '.join(CONFIG_PATHS.keys())}"
            )

        config_path = CONFIG_PATHS[scope]

        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Save config
        with open(config_path, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)

    def set_value(self, key_path: str, value: Any, scope: str = "local") -> None:
        """Set a configuration value by its dot-notation path.

        Args:
            key_path: Dot-notation path to the config value (e.g., 'ai.model')
            value: The value to set
            scope: Where to save the change ('local' or 'global')
        """
        # Split the path into parts
        parts = key_path.split(".")

        # Validate the path exists in our schema
        current = self.model_dump()
        for part in parts[:-1]:
            if part not in current:
                raise ValueError(f"Invalid config path: {key_path}")
            current = current[part]

        if parts[-1] not in current:
            raise ValueError(f"Invalid config path: {key_path}")

        # Load existing config for the specified scope
        config_path = CONFIG_PATHS[scope]
        if config_path.exists():
            with open(config_path, "r") as f:
                config_dict = yaml.safe_load(f) or {}
        else:
            config_dict = {}

        # Update the value
        current = config_dict
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

        # Save the updated config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False)

        # Reload the configuration
        global config
        config = Config.load()

    def get_value(self, key_path: str) -> Any:
        """Get a configuration value by its dot-notation path."""
        current = self.model_dump()
        for part in key_path.split("."):
            if part not in current:
                raise ValueError(f"Invalid config path: {key_path}")
            current = current[part]
        return current

    @classmethod
    def list_options(cls) -> List[Dict[str, str]]:
        """List all available configuration options with their descriptions."""
        options = []

        def extract_fields(model_class: type[BaseModel], prefix: str = ""):
            for field_name, field in model_class.model_fields.items():
                full_path = f"{prefix}.{field_name}" if prefix else field_name

                # Get the field type
                field_type = field.annotation

                # If it's a nested model
                if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                    extract_fields(field_type, full_path)
                else:
                    # Get the default value
                    if field.default_factory is not None:
                        default_value = field.default_factory()
                    else:
                        default_value = field.default

                    options.append(
                        {
                            "path": full_path,
                            "description": field.description or "",
                            "default": str(default_value),
                        }
                    )

        # Start with the main config class
        extract_fields(cls)
        return options


# Global configuration instance
config = Config.load()
