import os
import shutil
import subprocess
import tempfile
from typing import Optional, Tuple

import click

from core.cli.args_parser import argparse
from core.cli.cli import ApiKeyCLI, ModelsCLI, TemplatesCLI
from core.config.config import GitkConfig
from core.constants import HELP_TEXT
from core.generator import generate_commit_message
from core.utils import is_safe_filename


def get_git_path() -> str:
    path = shutil.which("git")
    if path is None:
        raise RuntimeError("git executable not found in PATH")
    return path


@click.group()
def cli() -> None:
    pass


@cli.command()
def init() -> None:
    config = GitkConfig()
    templates_cli = TemplatesCLI()
    models_cli = ModelsCLI("openrouter")
    api_key_cli = ApiKeyCLI()

    selected_model = models_cli.select_model()
    api_key = api_key_cli.setup_api_key(selected_model)
    template = templates_cli.setup_interactive()

    config.save_config(selected_model, template, api_key)
    click.secho("GitK initialized.", fg="green")


@cli.command(help=HELP_TEXT)
@click.option("--detailed", is_flag=True, help="Generate detailed commit message")
@click.option("--yes", "no_confirm", is_flag=True, default=False, help="Do not ask for confirmation")
@click.option("--split", is_flag=True, help="Commit each file separately")
@click.option("--template-file", type=click.Path(exists=True), help="Path to custom commit template")
@click.option("--template", type=str, help="Inline commit template")
@click.option("--instruction", type=str, help="Additional instruction for the model")
@click.argument("extra_git_flags", nargs=-1, type=str)
def commit(
    detailed: bool,
    no_confirm: bool,
    split: bool,
    template_file: Optional[str],
    template: Optional[str],
    instruction: Optional[str],
    extra_git_flags: Tuple[str, ...],
) -> None:
    config = GitkConfig()

    args = argparse.Namespace(
        detailed=detailed,
        instruction=instruction,
        template=template,
        template_file=template_file,
        init=False
    )

    git_path = get_git_path()

    def generate_commit(diff_input: str, no_confirm: bool, file_path: Optional[str] = None) -> None:
        commit_msg = generate_commit_message(args, config, diff_input)

        if no_confirm:
            click.echo(f"Committing{' ' + file_path if file_path else ''}...")
        else:
            click.echo("\n--- Commit message ---")
            click.echo(commit_msg)
            click.echo("----------------------")
            if not click.confirm("Do you want to continue?"):
                click.echo(f"Skipping {file_path if file_path else 'commit'}")
                return

        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp.write(commit_msg)
            tmp_path = tmp.name

        try:
            cmd = [git_path, "commit", "-F", tmp_path] + list(extra_git_flags)
            if file_path:
                if not is_safe_filename(file_path):
                    raise ValueError(f"Unsafe filename detected: {file_path}")
                cmd.append("--")
                cmd.append(file_path)
            subprocess.run(cmd, check=True) # noqa: S603
        finally:
            os.remove(tmp_path)

    if split:
        result = subprocess.run([git_path, "diff", "--cached", "--name-only"], capture_output=True, text=True) # noqa: S603
        staged_files = result.stdout.strip().splitlines()

        if not staged_files:
            click.echo("Index is empty. Nothing to commit.")
            return

        for file in staged_files:
            if not is_safe_filename(file):
                click.echo(f"Unsafe filename skipped: {file}")
                continue
            result = subprocess.run([git_path, "diff", "--cached", "--", file], capture_output=True, text=True) # noqa: S603
            diff = result.stdout.strip()
            if not diff:
                click.echo(f"Diff is empty for file: {file}")
                continue
            click.echo(f"\n--- Generating commit message for file: {file} ---")
            generate_commit(diff, no_confirm, file)
    else:
        result = subprocess.run([git_path, "diff", "--cached"], capture_output=True, text=True) # noqa: S603
        full_diff = result.stdout.strip()

        if not full_diff:
            click.echo("Index is empty. Nothing to commit.")
            return

        generate_commit(full_diff, no_confirm)


@cli.group()
def update() -> None:
    pass


@update.command("models")
def update_models() -> None:
    models_cli = ModelsCLI("openrouter")
    models_cli.refresh_models_list()
    click.secho("Models list updated.", fg="green")


if __name__ == "__main__":
    cli()