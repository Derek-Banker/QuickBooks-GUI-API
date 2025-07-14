# src/quickbooks_gui_api/__main__.py

"""Unified command line interface for QuickBooks GUI automation and setup."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from quickbooks_gui_api.gui_api import (
    QuickBookGUIAPI,
    DEFAULT_CONFIG_FOLDER_PATH,
    DEFAULT_CONFIG_FILE_NAME,
)
from quickbooks_gui_api.setup import Setup


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
def startup(config_dir: Path, config_file: str, no_kill_avatax: bool) -> None:
    """Launch QuickBooks, open a company, and log in."""

    api = QuickBookGUIAPI()
    api.startup(
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


@setup.command("set-credentials")
@click.option("--username", "-u", required=True, help="Username to encrypt and store")
@click.option("--password", "-p", required=True, help="Password to encrypt and store")
@click.option("--local-key-name", "-lkn", default=None, help="Environment variable name for the encryption key")
@click.option("--local-key-value", "-lkv", default=None, help="Encryption key value (direct input)")
@click.option(
    "--config-path",
    "-c-path",
    type=click.Path(path_type=Path),
    default=Path("configs/config.toml"),
    show_default=True,
    help="Path to config TOML",
)
@click.option(
    "--config-index",
    "-c-index",
    default="QuickBooksGUIAPI.secrets",
    show_default=True,
    help="Config section/table name",
)
@click.pass_context
def set_credentials(
    ctx: click.Context,
    username: str,
    password: str,
    local_key_name: str | None,
    local_key_value: str | None,
    config_path: Path,
    config_index: str,
) -> None:
    """Set credentials in the config file."""

    if (local_key_name is None) == (local_key_value is None):
        raise click.UsageError(
            "Exactly one of (--local-key-name | -lkn) or (--local-key-value | -lkv) must be provided."
        )

    logging.basicConfig(
        level=getattr(logging, ctx.obj["log_level"]),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    setup_obj = Setup(config_index=config_index)
    try:
        setup_obj.set_credentials(
            username=username,
            password=password,
            local_key_name=local_key_name,
            local_key_value=local_key_value,
            config_path=config_path,
        )
        click.echo("Credentials set successfully.")
    except Exception as e:  # pragma: no cover - CLI
        logging.error(f"Operation failed: {e}")
        sys.exit(2)


@setup.command("prompt-credentials")
@click.option("--local-key-name", "-lkn", default=None, help="Environment variable name for the encryption key")
@click.option("--local-key-value", "-lkv", default=None, help="Encryption key value (direct input)")
@click.option(
    "--config-path",
    "-c-path",
    type=click.Path(path_type=Path),
    default=Path("configs/config.toml"),
    show_default=True,
    help="Path to config TOML",
)
@click.option(
    "--config-index",
    "-c-index",
    default="QuickBooksGUIAPI.secrets",
    show_default=True,
    help="Config section/table name",
)
@click.pass_context
def set_credentials_prompt(
    ctx: click.Context,
    local_key_name: str | None,
    local_key_value: str | None,
    config_path: Path,
    config_index: str,
) -> None:
    """Prompt for credentials and set the config file."""

    username = click.prompt("Username")
    password = click.prompt(
        "Password",
        hide_input=True,
        confirmation_prompt=True,
    )

    if (local_key_name is None) == (local_key_value is None):
        raise click.UsageError(
            "Exactly one of (--local-key-name | -lkn) or (--local-key-value | -lkv) must be provided."
        )

    logging.basicConfig(
        level=getattr(logging, ctx.obj["log_level"]),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    setup_obj = Setup(config_index=config_index)
    try:
        setup_obj.set_credentials(
            username=username,
            password=password,
            local_key_name=local_key_name,
            local_key_value=local_key_value,
            config_path=config_path,
        )
        click.echo("Credentials set successfully.")
    except Exception as e:  # pragma: no cover - CLI
        logging.error(f"Operation failed: {e}")
        sys.exit(2)


@setup.command("verify-credentials")
@click.option("--local-key-name", "-lkn", default=None, help="Environment variable name for the encryption key")
@click.option("--local-key-value", "-lkv", default=None, help="Encryption key value (direct input)")
@click.option(
    "--config-path",
    "-c-path",
    type=click.Path(path_type=Path),
    default=Path("configs/config.toml"),
    show_default=True,
    help="Path to config TOML",
)
@click.option(
    "--config-index",
    "-c-index",
    default="QuickBooksGUIAPI.secrets",
    show_default=True,
    help="Config section/table name",
)
@click.pass_context
def verify_credentials(
    ctx: click.Context,
    local_key_name: str | None,
    local_key_value: str | None,
    config_path: Path,
    config_index: str,
) -> None:
    """Verify credentials using the provided key."""

    if (local_key_name is None) == (local_key_value is None):
        raise click.UsageError(
            "Exactly one of --local-key-name or --local-key-value must be provided."
        )

    logging.basicConfig(
        level=getattr(logging, ctx.obj["log_level"]),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    setup_obj = Setup(config_index=config_index)
    try:
        valid = setup_obj.verify_credentials(
            local_key_name=local_key_name,
            local_key_value=local_key_value,
            config_path=config_path,
        )
        if valid:
            click.echo("Key is valid.")
            sys.exit(0)
        else:
            click.echo("Key is INVALID.")
            sys.exit(1)
    except Exception as e:  # pragma: no cover - CLI
        logging.error(f"Operation failed: {e}")
        sys.exit(2)


if __name__ == "__main__":  # pragma: no cover - CLI
    main()

