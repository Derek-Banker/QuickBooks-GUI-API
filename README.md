# QuickBooks GUI API

This project provides automation helpers for QuickBooks Desktop.  It exposes a
single command line interface `qb-cli` which bundles multiple utilities.

## CLI Usage

Run `qb-cli` followed by one of the modules and commands:

```
# GUI automation
qb-cli gui startup [--config-dir PATH] [--config-file NAME] [--no-avatax]
qb-cli gui shutdown

# Configuration management
qb-cli setup set-credentials --username USER --password PASS \
       (--local-key-name NAME | --local-key-value VALUE) [--config-path PATH]
qb-cli setup verify-credentials (--local-key-name NAME | --local-key-value VALUE)
```

The old `setup_cli.py` entry point now simply forwards to this unified CLI for
backwards compatibility.
