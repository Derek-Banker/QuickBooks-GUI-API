import argparse
import sys
import logging
from pathlib import Path

from src.quickbooks_gui_api.setup import Setup  # <-- Replace with your actual module/package name

def main():
    parser = argparse.ArgumentParser(
        description="Manage encrypted credentials in your config TOML."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: set-credentials
    set_parser = subparsers.add_parser("set-credentials", help="Set credentials in the config file")
    set_parser.add_argument("--username", required=True, help="Username to encrypt and store")
    set_parser.add_argument("--password", required=True, help="Password to encrypt and store")
    group = set_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--local-key-name", help="Environment variable name for the encryption key")
    group.add_argument("--local-key-value", help="Encryption key value (direct input)")
    set_parser.add_argument("--config-path", type=Path, default=Path("configs/config.toml"), help="Path to config TOML")
    set_parser.add_argument("--config-index", default="secrets", help="Config section/table name")

    # Subcommand: verify-credentials
    verify_parser = subparsers.add_parser("verify-credentials", help="Verify credentials using the provided key")
    group2 = verify_parser.add_mutually_exclusive_group(required=True)
    group2.add_argument("--local-key-name", help="Environment variable name for the encryption key")
    group2.add_argument("--local-key-value", help="Encryption key value (direct input)")
    verify_parser.add_argument("--config-path", type=Path, default=Path("configs/config.toml"), help="Path to config TOML")
    verify_parser.add_argument("--config-index", default="secrets", help="Config section/table name")

    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Instantiate Setup
    setup = Setup(config_index=args.config_index)

    try:
        if args.command == "set-credentials":
            setup.set_credentials(
                username=args.username,
                password=args.password,
                local_key_name=args.local_key_name,
                local_key_value=args.local_key_value,
                config_path=args.config_path,
            )
            print("Credentials set successfully.")

        elif args.command == "verify-credentials":
            valid = setup.verify_credentials(
                local_key_name=args.local_key_name,
                local_key_value=args.local_key_value,
                config_path=args.config_path,
            )
            if valid:
                print("Key is valid.")
                sys.exit(0)
            else:
                print("Key is INVALID.")
                sys.exit(1)
    except Exception as e:
        logging.error(f"Operation failed: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
