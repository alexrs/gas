import os
import json
import re
import time
from typing import Optional, Dict

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from rich.console import Console
from rich.status import Status

from gas.core.config import config

load_dotenv()
console = Console()


class AIClient:
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        """Initialize the AI client with Hugging Face Inference API.

        Args:
            api_key: HuggingFace API key. Defaults to HUGGINGFACE_API_KEY env var.
            max_retries: Maximum number of retries for API calls.
        """
        self.api_key = api_key or _get_api_key()
        self.client = InferenceClient(
            provider="cohere",  # Using Cohere via HF Inference API
            api_key=self.api_key,
        )
        self.max_retries = max_retries

    def generate(
        self, prompt: str, max_tokens: Optional[int] = None, temperature: Optional[float] = None
    ) -> str:
        """Generate text using the AI model with retry logic.

        Args:
            prompt: The input prompt for generation
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (0.0 to 1.0)

        Returns:
            Generated text response

        Raises:
            ValueError: If the API call fails after max retries
        """
        last_error = None

        # Use config values if not overridden
        max_tokens = max_tokens or config.ai.max_tokens
        temperature = temperature or config.ai.temperature

        thinking_emoji = "🤖" if config.user.emoji_enabled else ""
        retry_emoji = "🔄" if config.user.emoji_enabled else ""
        error_emoji = "❌" if config.user.emoji_enabled else ""

        with Status(f"[bold yellow]{thinking_emoji} Thinking...", spinner="dots") as status:
            for attempt in range(self.max_retries):
                try:
                    status.update(
                        f"[bold yellow]{thinking_emoji} Thinking... (Attempt {attempt + 1}/{self.max_retries})"
                    )

                    # Add language preference to prompt if not English
                    if config.user.language != "en":
                        prompt = f"Please respond in {config.user.language} language.\n\n{prompt}"

                    completion = self.client.chat.completions.create(
                        model=config.ai.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    return completion.choices[0].message.content

                except Exception as e:
                    last_error = e
                    if attempt < self.max_retries - 1:
                        wait_time = 1.5**attempt  # Exponential backoff
                        status.update(
                            f"[yellow]{retry_emoji} Retrying... ({attempt + 1}/{self.max_retries}): {str(e)}"
                        )
                        time.sleep(wait_time)
                    else:
                        status.update(f"[red]{error_emoji} Failed to generate response")
                        console.print(f"[red]Max retries reached. Last error: {str(e)}[/red]")

        raise ValueError(
            f"Failed to generate response after {self.max_retries} attempts: {str(last_error)}"
        )

    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from potentially messy LLM output."""
        # Try to find JSON in code blocks
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        # Try to find raw JSON
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))

        raise ValueError("Could not extract valid JSON from response")


def _get_api_key() -> str:
    """Get the Hugging Face API key from environment variables."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")

    if not api_key:
        console.print("[red]Error: HUGGINGFACE_API_KEY environment variable not set[/red]")
        console.print("Please set your Hugging Face API key:")
        console.print("export HUGGINGFACE_API_KEY='your-api-key'")
        console.print("or add it to your .env file:")
        console.print("HUGGINGFACE_API_KEY='your-api-key'")
        raise ValueError("HUGGINGFACE_API_KEY not set")

    return api_key


def get_ai_client(api_key: Optional[str] = None, max_retries: int = 3) -> AIClient:
    """Get an instance of the AI client."""
    return AIClient(api_key=api_key, max_retries=max_retries)
