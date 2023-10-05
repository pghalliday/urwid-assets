# urwid-assets

## Prerequisites

- MacOS or Linux (I don't think Windows terminals are supported by Urwid)
- [Poetry](https://python-poetry.org/docs/)

Create the default environment with dependencies installed with:

```shell
poetry install --sync
```

Start a Poetry shell using:

```shell
poetry shell
```

## Usage

From a Poetry shell, show help with

```shell
urwid-assets
```

Start the UI with:

```shell
urwid-assets ui
```

Export the raw JSON (decrypt)

```shell
urwid-assets export [EXPORT_FILE=export.json]
```

Import from exported JSON (encrypt)

```shell
urwid-assets import [EXPORT_FILE=export.json]
```

By default, data, salt and log files will be created under `~/.urwid/` but these paths can be configured through the CLI
options

## TODO

- field validation in config dialogs
  - date time
  - integer
  - decimal
- delete assets/rates on deletion of symbol (after confirm)
  - Or block the delete with a useful error report
- prevent add asset unless there is at least one symbol
  - Or better still allow add symbol from add asset dialog
- prevent add rate unless there is at least one symbol (2?)
  - Or better still allow add symbol from add rate dialog
- config file instead of (or in addition to) command line options
- change passphrase
- more documentation
- fix move list item focus stickiness in table (scroll and not move?)
- mouse click handling (double clicks) and generally better usability (enter to submit or change field, tabbing, etc)
