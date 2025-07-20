_DEFAULT_COMMIT_TEMPLATE: str = """ Requirements:
    - Use format: type: brief description
    - Types: feat, fix, docs, style, refactor, test, chore
    - Commit message must start with lowercase letter!

    Examples:
    feat: add login validation
    fix: handle null user data
    docs: update setup guide

    Git Diff:

"""

DETAILED_INSTRUCTIONS: str = """ Write a git commit message with title and detailed body for this git diff. Examples:
    feat: add user login flow

    - introduce new login form component
    - connect to auth service
    - handle basic validation \n
"""

SINGLE_INSTRUCTIONS: str = "Write ONLY a single line commit message for this git diff.\n\n"

PROVIDER_INSTRUCTIONS = {
    "openrouter": "OpenRouter → Get your key at: https://openrouter.ai",
}


CONTEXT_SCORE_LARGE = 20
CONTEXT_SCORE_HIGH = 15 
CONTEXT_SCORE_MEDIUM = 10
CONTEXT_SCORE_LOW = 5 

TOP_TIER_MODELS = {
    'gpt-4': 25,
    'claude': 25,
    'gemini': 20,
    'llama-3': 20,
    'mixtral': 18,
    'qwen': 15,
    'deepseek': 15,
    'phi-3': 12,
    'mistral': 12,
}

SIZE_INDICATORS = {
    '405b': 15,
    '300b': 14,
    '175b': 13,
    '70b': 12,
    '34b': 10,
    '13b': 8,
    '8b': 7,
    '7b': 6,
    '3b': 4,
    '1b': 2,
}

LOW_QUALITY_INDICATOR_PENALTY = 5
LOW_QUALITY_INDICATORS = ['test', 'experimental', 'preview', 'alpha', 'beta', 'dev']