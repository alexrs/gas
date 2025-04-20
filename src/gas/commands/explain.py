import textwrap
from rich.console import Console
from rich.panel import Panel
from rich.status import Status

from gas.core.ai import get_ai_client
from gas.core.git import parse_git_diff
from gas.core.config import config

console = Console()

def explain_diff(diff_content: str, detailed: bool = False) -> None:
    """Explain the Git diff using AI.

    Args:
        diff_content: The raw git diff content
        detailed: Whether to provide a detailed explanation
    """
    if not diff_content.strip():
        console.print("[yellow]No changes to explain[/yellow]")
        return

    # Parse the git diff to get structured changes
    with Status("[bold blue]📝 Analyzing changes...", spinner="dots") as status:
        changes = parse_git_diff(diff_content)

        # Prepare the prompt for the AI
        prompt = _build_explanation_prompt(changes, detailed)

    try:
        # Get AI explanation
        client = get_ai_client()
        response = client.generate(
            prompt=prompt,
            max_tokens=config.ai.max_tokens,
            temperature=config.ai.temperature,
        )

        # Display the explanation
        console.print(Panel(
            response,
            title="[bold green]✨ Changes Explained[/bold green]",
            border_style="green"
        ))
    except Exception as e:
        console.print(f"[red]❌ Error explaining changes: {str(e)}[/red]")

def _build_explanation_prompt(
    changes: str,
    detailed: bool = False,
    language: str = "en"
) -> str:
    """Build an AI prompt for explaining Git diffs."""
    # Language instruction for non-English responses
    language_instruction = (
        "" if language.lower().startswith("en")
        else f"Please respond in {language}."
    )

    # Core instruction for the AI
    core_instruction = textwrap.dedent(f"""
        {language_instruction}
        You are an expert Git assistant. Analyze the following Git diff and explain the
        changes in a clear, structured way that helps developers understand them quickly.

        Your explanation should include:
        1. **Summary**: A concise one- or two-sentence overview of the main purpose.
        2. **Files Affected**: A list of key files or directories changed.
        3. **Details**: For each change, describe:
           - What was modified or added
           - Why the change was made
        4. **Impact & Risks**: Potential side effects, regressions, or areas to review.
        5. **Best Practices / Patterns**: Any design patterns, conventions, or best practices used.
    """)

    # Detailed instructions, if requested
    detailed_section = ""
    if detailed:
        detailed_section = textwrap.dedent("""
            -- Detailed Analysis --
            6. **Technical Specifics**: Explain complex logic, edge cases, and performance considerations.
            7. **Dependencies & Affected Areas**: Note related modules or features that might be impacted.
            8. **References**: Link to relevant documentation, code comments, or design docs if available.
        """)

    # Assemble final prompt
    prompt = f"{core_instruction.strip()}\n{detailed_section.strip()}\n\nGit diff:\n{changes.strip()}"
    return prompt
