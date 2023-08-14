# urwid-assets

## Prerequisites

- MacOS or Linux (I don't think Windows terminals are supported by Urwid)
- [Anaconda](https://docs.anaconda.com/free/anaconda/install/index.html)

Then create a `conda` environment and install dependencies with:

```shell
conda env create -f environment.yml
```

Activate the environment with:

```shell
conda activate urwid-assets
```

After adding new dependencies to `environment.yml`, update the environment with:

```shell
conda env update --file environment.yml --prune
```

## Usage

Show CLI help with:

```shell
python main.py -h
```

Start the UI with:

```shell
python main.py ui
```

Export the raw JSON (decrypt)

```shell
python main.py export [EXPORT_FILE=export.json]
```

Import from exported JSON (encrypt)

```shell
python main.py import [EXPORT_FILE=export.json]
```

By default, data, salt and log files will be created under `~/.urwid/` but these paths can be configured through the CLI options


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
