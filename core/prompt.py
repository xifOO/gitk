from typing import Optional

from core.constants import (
    _DEFAULT_COMMIT_TEMPLATE,
    DETAILED_INSTRUCTIONS,
    SINGLE_INSTRUCTIONS,
)


def get_commit_instruction(
        diff: str,
        detailed: bool = False,
        commit_template: Optional[str] = None,
        instruction: Optional[str] = None
) -> str:
    if not diff.strip():
        raise ValueError("Empty diff. No changes to analyze.")
    
    _commit_template: str = commit_template or _DEFAULT_COMMIT_TEMPLATE

    if detailed:
        result = DETAILED_INSTRUCTIONS + _commit_template + diff
    else:
        result = SINGLE_INSTRUCTIONS + _commit_template + diff
    
    if instruction:
        result += f"\n\nUser instruction: {instruction}"
    
    return result