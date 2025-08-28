# src/quickbooks_gui_api/__main__.py

"""Unified command line interface for QuickBooks GUI automation and setup."""

from __future__ import annotations

from pathlib import Path

import click

from quickbooks_gui_api.gui_api import (
    QuickBookGUIAPI,
    DEFAULT_CONFIG_FOLDER_PATH,
    DEFAULT_CONFIG_FILE_NAME,
)


@click.group()
def main() -> None:
    """CLI for QuickBooks GUI automation and setup utilities."""


@main.group()
def gui() -> None:
    """QuickBooks GUI automation commands."""


@gui.command()
@click.option(
    "--config-dir",
    "-c-dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_CONFIG_FOLDER_PATH,
    show_default=True,
    help="Where to look for config.toml",
)
@click.option(
    "--config-file",
    "-c-file",
    default=DEFAULT_CONFIG_FILE_NAME,
    show_default=True,
    help="Name of the TOML file to load",
)
@click.option(
    "--no-kill-avatax",
    "-nka",  
    is_flag=True,
    help="Don't kill Avalara processes after login",
)
def startup(
        username: str,
        password: str,
        config_dir: Path, 
        config_file: str, 
        no_kill_avatax: bool
    ) -> None:
    """Launch QuickBooks, open a company, and log in."""

    api = QuickBookGUIAPI()
    api.startup(
        username=username,
        password=password,
        config_directory=config_dir,
        config_file_name=config_file,
        kill_avatax=not no_kill_avatax,
    )


@gui.command()
def shutdown() -> None:
    """Terminate all QuickBooks processes."""
    api = QuickBookGUIAPI()
    api.shutdown()


@main.group()
@click.option(
    "--log-level",
    "-ll",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    show_default=True,
)
@click.pass_context
def setup(ctx: click.Context, log_level: str) -> None:  # pragma: no cover - CLI
    """Manage encrypted credentials."""

    ctx.ensure_object(dict)
    ctx.obj["log_level"] = log_level



if __name__ == "__main__":  # pragma: no cover - CLI
    main()

