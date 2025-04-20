from pathlib import Path
from typing import Iterator
import pytest
import tempfile
from gas.core.config import Config

@pytest.fixture
def temp_config_dir() -> Iterator[Path]:
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def mock_config_paths(temp_config_dir: Path, monkeypatch) -> dict[str, Path]:
    """Override config paths to use temporary directory."""
    test_paths = {
        'local': temp_config_dir / '.gas.yaml',
        'global': temp_config_dir / 'config.yml',
    }
    monkeypatch.setattr('gas.core.config.CONFIG_PATHS', test_paths)

    # Reset the global config instance with mocked paths
    monkeypatch.setattr('gas.core.config.config', Config())

    return test_paths

@pytest.fixture
def sample_diff() -> str:
    """Return a sample git diff for testing."""
    return """diff --git a/src/main.py b/src/main.py
index abc123..def456 100644
--- a/src/main.py
+++ b/src/main.py
@@ -10,6 +10,8 @@ def main():
     print("Hello World")
+    # Add new feature
+    print("New feature")

-    # Remove old code
-    old_function()
+    # Add better implementation
+    new_function()
"""