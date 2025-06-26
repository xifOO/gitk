_DEFAULT_COMMIT_TEMPLATE: str = """

Requirements:
    - Use format: type: brief description
    - Types: feat, fix, docs, style, refactor, test, chore
    - Maximum 50 characters total
    - No explanations, no markdown, no extra text
    - Just the commit message line
    - Commit message must start with lowercase letter!

    Examples:
    feat: add login validation
    fix: handle null user data
    docs: update setup guide

    Git Diff:

"""


PROVIDER_INSTRUCTIONS = {
    "openrouter": "OpenRouter → Получите ключ на: https://openrouter.ai",
}