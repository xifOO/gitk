from typing import Optional


_DEFAULT_COMMIT_TEPLATE: str = """

Requirements:
    - Use format: type: brief description
    - Types: feat, fix, docs, style, refactor, test, chore
    - Maximum 50 characters total
    - No explanations, no markdown, no extra text
    - Just the commit message line
    - Commit message must start with lowercase letter

    Examples:
    feat: add login validation
    fix: handle null user data
    docs: update setup guide

    Git Diff:

"""


def get_commit_instruction(
        diff: str,
        detailed: bool = False,
        commit_template: Optional[str] = None,
        instruction: Optional[str] = None
):
    if not diff.strip():
        raise ValueError("Diff пустой. Убедитесь что есть изменения для commit.")
    
    _commit_template: str = commit_template or _DEFAULT_COMMIT_TEPLATE

    if detailed:
        result = "Write a git commit message with title and detailed body for this git diff.\n" + _commit_template + diff
    else:
        result = "Write ONLY a single line commit message for this git diff.\n\n" + _commit_template + diff
    
    if instruction:
        result += f"\n\nUser instruction: {instruction}"
    
    return result