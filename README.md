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

- split rates from assets to allow display of different currencies independent of data source pairs
    - apply dijkstra for shortest path between pairs
    - apply weights (cost) for less desirable conversions (eg, higher cost for less liquid pairs)
- fix move list item focus stickiness in table (scroll and not move?)
- delete assets on deletion of data source (after confirm)
- prevent add asset unless there is at least one data source
- change passphrase
- more documentation
- mouse click handling (double clicks)
- field validation in config dialogs
