# GitK

**GitK** is a CLI tool built with Python 3.12 that leverages AI to generate meaningful commit messages based on your staged changes. It uses the OpenRouter provider to select AI models, helping you write better commits effortlessly.

---

## Features

- AI-powered commit message generation from staged diffs  
- Support for detailed and concise commit messages  
- Customizable commit message templates  
- Option to commit changes file-by-file for atomic commits (`--split`)  
- Seamless integration with Git workflows  

---

## Installation

> ⚠️ **Note:** An official installer or package is not available yet.  
> For now, clone the repo and install dependencies manually.

```bash
git clone https://github.com/xifOO/gitk.git
cd gitk

python3.12 -m venv env
source env/bin/activate  # Linux/macOS
# env\Scripts\activate   # Windows

pip install -r requirements.txt
```

---

## Key Dependencies

- click — for building the CLI interface
- requests - for HTTP requests
- pydantic — for data validation and settings management
- questionary — for interactive CLI prompts
(Full list of dependencies is available in requirements.txt)


--- 


## Usage
```bash
gitk commit [OPTIONS] [EXTRA_GIT_FLAGS]...
```
Generate AI-based commit messages from your staged changes.


## Options
 
 - [detailed]
   Generate a more detailed commit message, useful for complex diffs.
- [yes]
  Skip confirmation prompts and commit automatically with the generated message.
- [split]
  Generate and commit messages for each staged file separately for atomic commits.
- [template-file] PATH
  Use a custom commit message template file with placeholders like {{diff}} and {{instruction}}.
- [template] TEXT
  Inline template string that overrides the default template.
- [instruction] TEXT
  Provide additional context or instructions to guide AI when generating messages.
- [EXTRA_GIT_FLAGS] ...
  Pass extra flags directly to git commit (e.g., --signoff, --amend).

# Examples
  ``` bash
  gitk commit --detailed
  gitk commit --split --template-file=my_template.txt
  gitk commit --template="Change summary: {{diff}}" --yes
  gitk commit --instruction="Write in imperative tense"
  ```

---

## Configuration

  Before using GitK, run:


  ```bash
  gitk init
  ```
  This will guide you through setting up API keys, selecting AI models, and configuring your commit message templates.

---

## Logging

Errors and important events are logged to:
```bash
~/.gitk_config/logs/gitk.log
```

This helps in troubleshooting without cluttering your CLI output.

