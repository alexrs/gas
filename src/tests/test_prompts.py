from gas.commands.explain import _build_explanation_prompt
from gas.commands.commit import _build_commit_prompt
from gas.core.config import Config

def test_explanation_prompt_english():
    """Test explanation prompt in English."""

    diff = """diff --git a/src/main.py b/src/main.py
@@ -1,3 +1,4 @@
+import sys
 def hello():
-    print("Hello")
+    print("Hello, World!")
"""

    prompt = _build_explanation_prompt(diff, detailed=False, language="en")
    assert "you are an expert git assistant." in prompt.lower()
    assert "language prompt" not in prompt.lower()  # No language prompt for English

def test_explanation_prompt_spanish():
    """Test explanation prompt in Spanish."""
    diff = """diff --git a/src/main.py b/src/main.py
@@ -1,3 +1,4 @@
+import sys
 def hello():
-    print("Hello")
+    print("Hello, World!")"""

    prompt = _build_explanation_prompt(diff, detailed=False, language="es")
    assert "es" in prompt.lower()
    assert diff in prompt

def test_explanation_prompt_detailed():
    """Test detailed explanation prompt."""
    diff = "sample diff"

    prompt_simple = _build_explanation_prompt(diff, detailed=False, language="en")
    prompt_detailed = _build_explanation_prompt(diff, detailed=True, language="en")

    assert len(prompt_detailed) > len(prompt_simple)
    assert "detailed" in prompt_detailed.lower()

def test_commit_prompt_english():
    """Test commit message prompt in English."""

    diff = """diff --git a/src/main.py b/src/main.py
@@ -1,3 +1,4 @@
+import sys
 def hello():
-    print("Hello")
+    print("Hello, World!")"""

    prompt = _build_commit_prompt(diff, language="en")
    assert "generate a clear and concise commit message" in prompt.lower()
    assert "language prompt" not in prompt.lower()  # No language prompt for English

def test_commit_prompt_french():
    """Test commit message prompt in French."""

    diff = """diff --git a/src/main.py b/src/main.py
@@ -1,3 +1,4 @@
+import sys
 def hello():
-    print("Hello")
+    print("Hello, World!")"""

    prompt = _build_commit_prompt(diff, language="fr")
    assert "fr" in prompt.lower()
    assert diff in prompt

def test_commit_prompt_conventional():
    """Test conventional commit message prompt."""
    diff = "sample diff"

    prompt = _build_commit_prompt(diff, commit_type="feat")
    assert "conventional commit format" in prompt.lower()
    assert "feat([scope]): description" in prompt.lower()