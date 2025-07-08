# src/quickbooks_gui_api/__main__.py

import argparse
from pathlib import Path
from quickbooks_gui_api.gui_api import (
    QuickBookGUIAPI,
    DEFAULT_CONFIG_FOLDER_PATH,
    DEFAULT_CONFIG_FILE_NAME,
)

def main():
    parser = argparse.ArgumentParser(
        prog="qb-gui",
        description="Start or stop the QuickBooks GUI automation."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # startup subcommand
    p_start = sub.add_parser("startup", help="Launch QuickBooks, open a company, and log in")
    p_start.add_argument(
        "--config-dir",
        type=Path,
        default=DEFAULT_CONFIG_FOLDER_PATH,
        help="Where to look for config.toml",
    )
    p_start.add_argument(
        "--config-file",
        default=DEFAULT_CONFIG_FILE_NAME,
        help="Name of the TOML file to load",
    )
    p_start.add_argument(
        "--no-avatax",
        action="store_false",
        dest="fuck_avatax",
        help="Don’t kill Avalara processes after login",
    )

    # shutdown subcommand
    sub.add_parser("shutdown", help="Terminate all QuickBooks processes")

    args = parser.parse_args()

    api = QuickBookGUIAPI()

    if args.command == "startup":
        api.startup(
            config_directory=args.config_dir,
            config_file_name=args.config_file,
            fuck_avatax=args.fuck_avatax,
        )
    elif args.command == "shutdown":
        api.shutdown()

if __name__ == "__main__":
    main()
