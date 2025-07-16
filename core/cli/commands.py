import os
import click

from core.cli.cli import ApiKeyCLI, ModelsCLI, TemplatesCLI
from core.config.config import GitkConfig


@click.group()
def cli():
    pass


@cli.command()
def init():
    config = GitkConfig()
    templates_cli = TemplatesCLI()
    models_cli = ModelsCLI()
    api_key_cli = ApiKeyCLI()

    selected_model = models_cli.select_model()
    api_key = api_key_cli.setup_api_key(selected_model)
    template = templates_cli.setup_interactive()

    config.save_config(selected_model, template, api_key)
    click.secho("GitK initialized.", fg="green")


@cli.command()
@click.option("--detailed", is_flag=True, help="Generate detailed commit message")
@click.option("--yes", "no_confirm", is_flag=True, default=False, help="Do not ask for confirmation")
@click.option("--split", is_flag=True, help="Commit each file separately")
@click.option("--template-file", type=click.Path(exists=True), help="Path to custom commit template")
@click.option("--template", type=str, help="Inline commit template")
@click.option("--instruction", type=str, help="Additional instruction for the model")
@click.argument("extra_git_flags", nargs=-1, type=str)
def commit(detailed, no_confirm, split, template_file, template, instruction, extra_git_flags):
    import tempfile
    import subprocess
    from core.config.config import GitkConfig
    from core.cli.args_parser import argparse

    config = GitkConfig()

    args = argparse.Namespace(
        detailed=detailed,
        instruction=instruction,
        template=template,
        template_file=template_file,
        init=False
    )

    def generate_commit(diff_input, no_confirm, file_path=None):
        from core.generator import generate_commit_message

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
            cmd = ["git", "commit", "-F", tmp_path] + list(extra_git_flags)
            if file_path:
                cmd.append("--")
                cmd.append(file_path)
            subprocess.run(cmd, check=True)
        finally:
            os.remove(tmp_path)

    if split:
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
        staged_files = result.stdout.strip().splitlines()

        if not staged_files:
            click.echo("Index is empty. Nothing to commit.")
            return

        for file in staged_files:
            result = subprocess.run(["git", "diff", "--cached", "--", file], capture_output=True, text=True)
            diff = result.stdout.strip()
            if not diff:
                click.echo(f"⚠️ Diff is empty for file: {file}")
                continue
            click.echo(f"\n--- Generating commit message for file: {file} ---")
            generate_commit(diff, no_confirm, file)
    else:
        result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
        full_diff = result.stdout.strip()

        if not full_diff:
            click.echo("Index is empty. Nothing to commit.")
            return

        generate_commit(full_diff, no_confirm)



@cli.group()
def update():
    pass


@update.command("models")
def update_models():
    models_cli = ModelsCLI()
    models_cli.refresh_models_list()
    click.secho("Models list updated.", fg="green")


if __name__ == "__main__":
    cli()