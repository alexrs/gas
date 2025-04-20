import pytest
import yaml

from gas.core.config import Config, AIConfig, UserConfig

def test_default_config():
    """Test default configuration values."""
    config = Config()
    assert isinstance(config.ai, AIConfig)
    assert isinstance(config.user, UserConfig)
    assert config.ai.model == "CohereLabs/c4ai-command-a-03-2025"
    assert config.ai.temperature == 0.7
    assert config.ai.max_tokens == 500
    assert config.user.language == "en"
    assert config.user.emoji_enabled is True

def test_config_load_empty(mock_config_paths):
    """Test loading configuration when no files exist."""
    config = Config.load()
    assert config.user.language == "en"  # Default value
    assert config.ai.model == "CohereLabs/c4ai-command-a-03-2025"  # Default value

def test_config_local_override(mock_config_paths):
    """Test that local config overrides global config."""
    # Create global config
    global_config = {
        'user': {'language': 'es'},
        'ai': {'temperature': 0.5}
    }
    mock_config_paths['global'].parent.mkdir(parents=True, exist_ok=True)
    with open(mock_config_paths['global'], 'w') as f:
        yaml.dump(global_config, f)

    # Create local config
    local_config = {
        'user': {'language': 'fr'}
    }
    with open(mock_config_paths['local'], 'w') as f:
        yaml.dump(local_config, f)

    config = Config.load()
    assert config.user.language == 'fr'  # Local override
    assert config.ai.temperature == 0.5  # From global
    assert config.ai.model == "CohereLabs/c4ai-command-a-03-2025"  # Default

def test_config_set_value(mock_config_paths):
    """Test setting configuration values."""
    config = Config.load()

    # Set a value in local config
    config.set_value('user.language', 'de', scope='local')

    # Reload config and verify
    config = Config.load()
    assert config.user.language == 'de'

    # Verify file contents
    with open(mock_config_paths['local'], 'r') as f:
        saved_config = yaml.safe_load(f)
    assert saved_config['user']['language'] == 'de'

def test_config_invalid_path():
    """Test handling of invalid configuration paths."""
    config = Config()
    with pytest.raises(ValueError):
        config.set_value('invalid.path', 'value')
    with pytest.raises(ValueError):
        config.get_value('invalid.path')

def test_config_type_validation(mock_config_paths):
    """Test validation of configuration value types."""
    config = Config.load()

    # Test valid values
    config.set_value('ai.temperature', 0.8)

    # Reload config and verify
    config = Config.load()
    assert config.ai.temperature == 0.8

    # Test invalid values
    with pytest.raises(ValueError):
        config.set_value('ai.temperature', 2.0)  # Out of range
    with pytest.raises(ValueError):
        config.set_value('ai.max_tokens', -1)  # Invalid value
