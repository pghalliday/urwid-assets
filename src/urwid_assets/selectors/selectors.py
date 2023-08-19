from datetime import datetime
from decimal import Decimal
from functools import reduce
from uuid import UUID

from urwid_assets.lib.dijkstra.dijkstra import Edge, dijkstra, Resolved, get_steps, UnreachableTarget
from urwid_assets.lib.redux.reselect import create_selector, SelectorOptions
from urwid_assets.state.saved.assets.assets import Asset
from urwid_assets.state.saved.data_sources.data_sources import DataSourceInstance
from urwid_assets.state.saved.rates.rates import Rate
from urwid_assets.state.saved.saved import Saved
from urwid_assets.state.saved.snapshots.snapshots import Snapshot, SnapshotAsset
from urwid_assets.state.saved.symbols.symbols import Symbol, get_symbol
from urwid_assets.state.state import State
from urwid_assets.state.ui.ui import UI, LoadedRate, get_loaded_rate, UnknownLoadedRate
from urwid_assets.ui.views.helpers.format import format_timestamp


def select_saved(state: State) -> Saved:
    return state.saved


def select_ui(state: State) -> UI:
    return state.ui


def _select_assets(saved: Saved) -> tuple[Asset, ...]:
    return saved.assets


select_assets = create_selector((select_saved,), _select_assets)


def _select_data_sources(saved: Saved) -> tuple[DataSourceInstance, ...]:
    return saved.data_sources


select_data_sources = create_selector((select_saved,), _select_data_sources)


def _select_rates(saved: Saved) -> tuple[Rate, ...]:
    return saved.rates


select_rates = create_selector((select_saved,), _select_rates)


def _select_snapshots(saved: Saved) -> tuple[Snapshot, ...]:
    return saved.snapshots


select_snapshots = create_selector((select_saved,), _select_snapshots)


def _select_symbols(saved: Saved) -> tuple[Symbol, ...]:
    return saved.symbols


select_symbols = create_selector((select_saved,), _select_symbols)


def _select_target_symbol_uuid(ui: UI, symbols: tuple[Symbol, ...]) -> UUID | None:
    target_symbol = ui.target_symbol
    if target_symbol is None:
        try:
            return symbols[0].uuid
        except IndexError:
            return None
    return target_symbol


select_target_symbol_uuid = create_selector((
    select_ui,
    select_symbols
), _select_target_symbol_uuid)


def _select_target_symbol_name(uuid: UUID | None, symbols: tuple[Symbol, ...]) -> str:
    if uuid is not None:
        return get_symbol(uuid, symbols).name
    return '[No Symbol]'


select_target_symbol_name = create_selector((
    select_target_symbol_uuid,
    select_symbols
), _select_target_symbol_name)


def _select_last_update_time(ui: UI) -> datetime | None:
    return ui.last_update_time


select_last_update_time = create_selector((select_ui,), _select_last_update_time)


def _select_timestamp(ui: UI) -> datetime | None:
    return ui.timestamp


select_timestamp = create_selector((select_ui,), _select_timestamp)


def _select_loaded_rates(ui: UI) -> tuple[LoadedRate, ...]:
    return ui.loaded_rates


select_loaded_rates = create_selector((select_ui,), _select_loaded_rates)


def _select_rate_edge(rate: Rate,
                      loaded_rates: tuple[LoadedRate, ...]) -> Edge[UUID, Decimal] | None:
    # filter out all rates with missing 'to' symbols (happens on
    # migration from saved version 0)
    if rate.to_symbol is None:
        return None
    # filter out all rates for which we have no rate loaded
    try:
        loaded_rate = get_loaded_rate(rate.uuid, loaded_rates)
    except UnknownLoadedRate:
        return None
    # filter out all rates that have an error (i.e. no rate)
    if loaded_rate.rate is None:
        return None
    return Edge(source=rate.from_symbol,
                target=rate.to_symbol,
                cost=rate.cost,
                ref=loaded_rate.rate)


def _select_resolved_rates(edges: tuple[Edge[UUID, Decimal], ...], target_symbol: UUID) -> Resolved[UUID, Decimal]:
    return dijkstra(
        source=target_symbol,
        edges=filter(lambda edge: edge is not None, edges)
    )


select_rate_edges = create_selector((
    select_rates,
    select_loaded_rates,
), _select_rate_edge, SelectorOptions(dimensions=(1,)))

select_resolved_rates = create_selector((
    select_rate_edges,
    select_target_symbol_uuid,
), _select_resolved_rates)


def _select_rate_from_source_symbol(source_symbol: UUID, resolved: Resolved[UUID, Decimal]) -> Decimal | None:
    # NB. the Dijkstra resolved list has paths from target to source here,
    # so we need to reverse the steps (this is ok as the shortest paths
    # are symmetrical, i.e. the shortest path from a to b is the reverse
    # of the shortest path from b to a)
    try:
        steps = get_steps(source_symbol, resolved)
    except UnreachableTarget:
        # the symbol is not reachable from the source
        return None
    return reduce(lambda acc, rate: acc * rate,
                  [step.ref if step.reversed else Decimal(1.0) / step.ref for step in reversed(steps)],
                  Decimal(1.0))


def _select_asset_with_rate(asset: Asset, resolved: Resolved[UUID, Decimal]) -> tuple[Asset, Decimal | None]:
    return asset, _select_rate_from_source_symbol(asset.symbol, resolved)


select_assets_with_rates = create_selector((
    select_assets,
    select_resolved_rates,
), _select_asset_with_rate, SelectorOptions(dimensions=(1,)))


def _select_rates_by_data_source(data_source: DataSourceInstance,
                                 rates: tuple[Rate, ...]) -> tuple[DataSourceInstance, tuple[Rate, ...]]:
    return (
        data_source,
        tuple(filter(lambda rate: rate.data_source == data_source.uuid, rates)),
    )


select_rates_by_data_source = create_selector((
    select_data_sources,
    select_rates,
), _select_rates_by_data_source, SelectorOptions(dimensions=(1,)))


def _select_new_snapshot_asset(asset_with_rate: tuple[Asset, Decimal | None]) -> SnapshotAsset:
    asset, rate = asset_with_rate
    return SnapshotAsset(
        uuid=asset.uuid,
        name=asset.name,
        amount=asset.amount,
        rate=rate,
    )


select_new_snapshot_assets = create_selector((
    select_assets_with_rates,
), _select_new_snapshot_asset, SelectorOptions(dimensions=(1,)))


def _select_resolved_timestamp(timestamp: datetime | None, last_update_time: datetime | None) -> datetime | None:
    if timestamp is not None:
        return timestamp
    if last_update_time is not None:
        return last_update_time
    return None


select_resolved_timestamp = create_selector((
    select_timestamp,
    select_last_update_time,
), _select_resolved_timestamp)

select_timestamp_text = create_selector((
    select_resolved_timestamp,
), format_timestamp)
