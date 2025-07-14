# QuickBooks GUI API

QuickBooks GUI API is a Python toolkit for automating common tasks in **QuickBooks Desktop**. It wraps the [pywinauto](https://pywinauto.readthedocs.io/) library to control the QuickBooks user interface and exposes both a command line interface and Python classes for automation scripts. The project can launch and log in to QuickBooks, manage encrypted credentials, and save invoices or reports to disk. **It is designed for Windows environments where QuickBooks Desktop is installed.**

## Features

- **Startup / Shutdown** – programmatically start QuickBooks, open a company file and log in, then gracefully terminate all QuickBooks processes when done.
- **Invoice Automation** – open invoices by number and export them as PDF files.
- **Report Automation** – open memorized reports and export them to CSV files.
- **Encrypted Credentials** – helper commands to store and verify login details encrypted in the project configuration.

## Installation
Install from PyPI:
```bash
pip install qb-gui-api
```

Ensure [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and QuickBooks Desktop are installed on the machine.
If working from source:
```bash
pip install -e .
```

## Command Line Interface

The package installs a single entry point `qb-cli` with two groups of commands: `gui` for controlling QuickBooks and `setup` for credential management.

```
Usage: qb-cli [GROUP] [COMMAND] [OPTIONS]
```

### GUI Commands

- `qb-cli gui startup [--config-dir PATH] [--config-file NAME] [--no-kill-avatax]`
  - Launch QuickBooks, open the configured company file and log in.
  - `--config-dir`  Location of the configuration directory (default `configs`)
  - `--config-file` TOML file name to load (default `config.toml`)
  - `--no-kill-avatax`  Do not terminate Avalara processes after login.

- `qb-cli gui shutdown`
  - Terminate all QuickBooks related processes.

### Setup Commands

- `qb-cli setup set-credentials --username USER --password PASS [--local-key-name NAME | --local-key-value VALUE] [--config-path PATH]`
  - Encrypt the provided username and password and store them in the configuration file.

- `qb-cli setup prompt-credentials [--local-key-name NAME | --local-key-value VALUE] [--config-path PATH]`
  - Interactively prompt for the username and password before storing them.

- `qb-cli setup verify-credentials [--local-key-name NAME | --local-key-value VALUE] [--config-path PATH]`
  - Validate that the encryption key is correct for the stored credentials.

## Example Usage

Below are minimal Python examples for exporting invoices and reports. They mirror the scripts found in `samples/`.

### Saving Invoices

```python
from pathlib import Path
from quickbooks_gui_api import QuickBookGUIAPI
from quickbooks_gui_api.apis import Invoices
from quickbooks_gui_api.models import Invoice

api = QuickBookGUIAPI()
app, window = api.startup()

invoice_list = [
    Invoice("1254", None, Path(r"C:\\Path\\To\\Output")),
    Invoice("2016", None, Path(r"C:\\Path\\To\\Output")),
]

invoice_api = Invoices(app, window)
invoice_api.save(invoice_list)

api.shutdown()
```

### Saving Reports

```python
from pathlib import Path
from quickbooks_gui_api import QuickBookGUIAPI
from quickbooks_gui_api.apis import Reports
from quickbooks_gui_api.models import Report

api = QuickBookGUIAPI()
app, window = api.startup()

report_list = [
    Report("Data Export - All Invoices - V 3", None, Path(r"C:\\Path\\To\\Output")),
    Report("A/P Aging Detail", None, Path(r"C:\\Path\\To\\Output")),
]

report_api = Reports(app, window)
report_api.save(report_list)

api.shutdown()
```

These snippets start QuickBooks, create objects for each invoice or report, and instruct the appropriate API to save them, then terminates all QuickBooks processes. See the `samples/` directory for more complete examples.

## Configuration
Configuration values are stored in `configs/config.toml`. Defaults live in `configs/defaults/defaults_qb-gui-api.toml`.
You can override any setting by editing the config file before running the CLI or automation scripts.

## License

This project is licensed under the Apache 2.0 License. See `LICENSE` for details.

## Trademark Notice

"QuickBooks" is a registered trademark of Intuit Inc. This project is not affiliated with Intuit and the author makes no claim of ownership or control over the QuickBooks trademark.