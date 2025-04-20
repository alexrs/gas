# gas ⛽ (Git AI Sidekick)

A command-line tool that brings AI-powered assistance to your Git workflow.

**Note:** This project is just a demo of how to use Cohere models with Hugging Face Inference Providers. For more information, check out [the docs.](https://huggingface.co/docs/inference-providers/en/providers/cohere)

## Features

- **Explain Changes** (`git diff | gas explain`): Get an AI-powered explanation of your Git changes in plain English
- **Smart Commit Messages** (`gas commit`): Generate meaningful commit messages based on your changes

## Installation

1. Install UV by following the instructions at [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/).

2. Clone the repository:
```bash
git clone https://github.com/alexrs/gas.git
cd gas
```

3. Install the package:
```bash
uv tool install . -e --force
```

## Setup

1. Get a Hugging Face API key from [Hugging Face](https://huggingface.co/settings/tokens)
2. Set your API key as an environment variable or in a .env file:
```bash
# export env variable
export HUGGINGFACE_API_KEY='your-api-key'

# or in .env
HUGGINGFACE_API_KEY='your-api-key'
```

## Configuration

gas supports both global and local configuration files:
- Global config: `~/.config/gas/config.yml`
- Local config: `.gas.yaml` (in your repository)

Local configuration takes precedence over global configuration. You can manage your configuration using the `gas config` commands:

```bash
# List all available configuration options
gas config list

# View current configuration
gas config get

# Get a specific setting
gas config get ai.model

# Set a value in local config
gas config set ai.model "your-model-name"

# Set a value in global config
gas config set user.language "es" --scope global
```

Available settings:
```yaml
ai:
  # Model to use for generation
  model: "CohereLabs/c4ai-command-a-03-2025"
  # Temperature for generation (0.0 to 1.0)
  temperature: 0.7
  # Maximum tokens to generate
  max_tokens: 500

user:
  # Language for explanations (ISO 639-1 code)
  # Examples: en, es, fr, de, ja, ko, zh
  language: "en"
  # Whether to show emojis in output
  emoji_enabled: true
```

## Usage

### Explain Changes

```bash
# Explan current diff
gas explain

# Explain staged changes
git diff --staged | gas explain

# Explain changes between commits
git diff HEAD~1 HEAD | gas explain

# Get a detailed explanation
git diff | gas explain --detailed
```

### Generate Commit Messages

```bash
# Generate a commit message for staged changes
gas commit

# Generate a conventional commit message
gas commit --type feat

# Generate without opening editor
gas commit --no-edit
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
