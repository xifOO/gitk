_DEFAULT_COMMIT_TEMPLATE: str = """ Requirements:
    - Use format: type: brief description
    - Types: feat, fix, docs, style, refactor, test, chore
    - Commit message must start with lowercase letter!
    - Title line under 50 chars

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
    - handle basic validation

    Note: The first line (commit title) should be no more than 50 characters. If it exceeds 50, Git may wrap it into the body.
"""

SINGLE_INSTRUCTIONS: str = (
    "Write ONLY a single line commit message for this git diff.\n\n"
)

HELP_TEXT: str = """Usage: gitk commit [OPTIONS] [EXTRA_GIT_FLAGS]...

Generate AI-powered commit messages based on staged changes.

Options:
  --detailed               Generate a more detailed commit message. Useful for
                           longer or more complex diffs.

  --yes                    Skip confirmation prompts and commit automatically
                           with the generated message.
                           (Same as: --no-confirm)

  --split                  Generate and commit messages for each staged file
                           separately. Useful for keeping commits atomic.

  --template-file PATH     Path to a custom commit message template file.
                           Template should contain placeholders like {{diff}}
                           and {{instruction}}.

  --template TEXT          Inline template string to use for the commit
                           message. Overrides default template.

  --instruction TEXT       Additional instruction or context to guide the AI
                           model when generating commit messages.

  EXTRA_GIT_FLAGS...       Any extra flags to be passed directly to `git commit`.
                           Example: --signoff, --amend, etc.

Description:
  The `gitk commit` command generates commit messages using AI, based on
  the staged diff. It supports both single commit mode (default) and split
  per-file commits with `--split`.

  The tool uses a configured model and template (set via `gitk init`) to
  automatically craft commit messages that follow best practices.

Examples:
  gitk commit --detailed
  gitk commit --split --template-file=my_template.txt
  gitk commit --template="Change summary: {{diff}}" --yes
  gitk commit --instruction="Write in imperative tense"

"""

PROVIDER_INSTRUCTIONS = {
    "openrouter": "OpenRouter → Get your key at: https://openrouter.ai",
}


CONTEXT_SCORE_LARGE = 20
CONTEXT_SCORE_HIGH = 15
CONTEXT_SCORE_MEDIUM = 10
CONTEXT_SCORE_LOW = 5

TOP_TIER_MODELS = {
    "gpt-4": 25,
    "claude": 25,
    "gemini": 20,
    "llama-3": 20,
    "mixtral": 18,
    "qwen": 15,
    "deepseek": 15,
    "phi-3": 12,
    "mistral": 12,
}

SIZE_INDICATORS = {
    "405b": 15,
    "300b": 14,
    "175b": 13,
    "70b": 12,
    "34b": 10,
    "13b": 8,
    "8b": 7,
    "7b": 6,
    "3b": 4,
    "1b": 2,
}

LOW_QUALITY_INDICATOR_PENALTY = 5
LOW_QUALITY_INDICATORS = ["test", "experimental", "preview", "alpha", "beta", "dev"]
