import logging
from dataclasses import dataclass
from typing import Callable, TypeVar, Generic
from uuid import UUID, uuid1

from urwid import WidgetWrap, Pile, Columns, Divider, ListBox, Widget, Text, SimpleFocusListWalker, AttrMap, Frame

from lib.widgets.selectable_text import SelectableText

DATA = TypeVar('DATA')

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Row(Generic[DATA]):
    uuid: UUID
    fields: tuple[str, ...]
    data: DATA


@dataclass(frozen=True)
class Column:
    weight: int
    name: str


@dataclass(frozen=True)
class _ColumnData:
    weight: int
    create_widget: Callable[[str], Widget]


def _create_cell_tuple(cell_data: tuple[_ColumnData, str]) -> tuple[str, int, Widget]:
    (column_data, text) = cell_data
    return 'weight', \
        column_data.weight, \
        column_data.create_widget(text)


class _Row(WidgetWrap, Generic[DATA]):
    _row: Row[DATA]

    def __init__(self, row: Row[DATA], column_params: tuple[_ColumnData, ...]):
        self._row = row
        fields = row.fields
        diff = len(column_params) - len(fields)
        if diff > 0:
            fields += tuple(u'' for _ in range(diff))
        cells = zip(column_params, fields)
        super().__init__(AttrMap(Columns(_create_cell_tuple(cell_data)
                                         for cell_data in cells),
                                 None,
                                 focus_map='reversed'))

    def get_row(self) -> Row[DATA]:
        return self._row


class _RowFactory(Generic[DATA]):
    _column_params: tuple[_ColumnData, ...]

    def __init__(self, column_params: tuple[_ColumnData, ...]):
        self._column_params = column_params

    def create(self, row: Row[DATA]) -> _Row[DATA]:
        return _Row(row, self._column_params)


def _create_row_factory(columns: tuple[Column, ...]) -> _RowFactory[DATA]:
    return _RowFactory(tuple(
        _ColumnData(column.weight, SelectableText if index == 0 else Text)
        for index, column in enumerate(columns)
    ))


@dataclass(frozen=True)
class _IndexChange:
    uuid: UUID
    new_index: int


def _create_header(columns: tuple[Column, ...]) -> Pile:
    (header_column_params, column_names) = zip(*tuple(
        (_ColumnData(column.weight, Text), column.name)
        for column in columns
    ))
    return Pile([
        _RowFactory(header_column_params).create(Row(uuid1(), column_names, None)),
        Divider(u'-'),
    ])


@dataclass(frozen=True)
class IndexedRow(Generic[DATA]):
    index: int
    row: Row[DATA]


class Diff(Generic[DATA]):
    _current_rows: dict[UUID, IndexedRow[DATA]]
    _next_rows: dict[UUID, IndexedRow[DATA]]

    def __init__(self, current_rows: tuple[Row[DATA], ...], next_rows: tuple[Row[DATA], ...]) -> None:
        self._current_rows = {row.uuid: IndexedRow(index, row)
                              for index, row in enumerate(current_rows)}
        self._next_rows = {row.uuid: IndexedRow(index, row)
                           for index, row in enumerate(next_rows)}

    def get_deleted(self) -> tuple[IndexedRow, ...]:
        return tuple(filter(self._is_deleted, self._current_rows.values()))

    def get_added(self) -> tuple[IndexedRow, ...]:
        return tuple(filter(self._is_added, self._next_rows.values()))

    def get_changed(self) -> tuple[tuple[IndexedRow, IndexedRow], ...]:
        return tuple((indexed_row, self._next_rows[indexed_row.row.uuid])
                     for indexed_row in filter(self._is_changed, self._current_rows.values()))

    def get_moved(self, new_rows: tuple[Row[DATA], ...]) -> tuple[tuple[int, int]]:
        moved = filter(self._has_moved, tuple((index, row) for index, row in enumerate(new_rows)))
        return tuple((index, self._next_rows[row.uuid].index) for index, row in moved)

    def _is_changed(self, indexed_row: IndexedRow[DATA]) -> bool:
        try:
            return not self._next_rows[indexed_row.row.uuid].row is indexed_row.row
        except KeyError:
            return False

    def _is_deleted(self, indexed_row: IndexedRow[DATA]) -> bool:
        return not self._next_rows.keys().__contains__(indexed_row.row.uuid)

    def _is_added(self, indexed_row: IndexedRow[DATA]) -> bool:
        return not self._current_rows.keys().__contains__(indexed_row.row.uuid)

    def _has_moved(self, index_and_row: tuple[int, Row[DATA]]) -> bool:
        index, row = index_and_row
        try:
            return self._next_rows[row.uuid].index != index
        except KeyError:
            return False


class Table(WidgetWrap, Generic[DATA]):
    _rows: tuple[Row[DATA], ...] = None
    _row_factory: _RowFactory
    _row_list: SimpleFocusListWalker

    def __init__(self,
                 columns: tuple[Column, ...],
                 initial_rows: tuple[Row[DATA], ...]):
        self._rows = initial_rows
        self._row_factory = _create_row_factory(columns)
        self._row_list = SimpleFocusListWalker([self._create_row(row)
                                                for row in self._rows])
        self._row_list.set_focus_changed_callback(self._on_focus_changed)
        super().__init__(Frame(ListBox(self._row_list),
                               _create_header(columns)))

    def _on_focus_changed(self, index: int):
        # LOGGER.info(u'TODO: _on_focus_changed: %s' % index)
        pass

    def _create_row(self, row: Row[DATA]) -> _Row:
        return self._row_factory.create(row)

    def get_focused(self) -> Row[DATA] | None:
        index = self._row_list.focus
        if index is None:
            return None
        else:
            return self._rows[index]

    def _get_focused_widget(self) -> _Row[DATA] | None:
        index = self._row_list.focus
        if index is None:
            return None
        else:
            return self._row_list[index]

    def update(self, rows: tuple[Row[DATA], ...]) -> None:
        if rows is not self._rows:
            # apply changes to list efficiently
            diff = Diff(self._rows, rows)
            # first update the changed items before the indices change
            for (current_indexed_row, next_indexed_row) in diff.get_changed():
                self._row_list[current_indexed_row.index] = self._create_row(next_indexed_row.row)
            # now remove the deleted items so that the added indices will be valid
            # we do this backwards to ensure that the indices are still valid after each delete
            deleted = diff.get_deleted()
            for indexed_row in reversed(deleted):
                del self._row_list[indexed_row.index]
            # record the currently focused item
            focused = self._get_focused_widget()
            # as dicts are ordered the added list should be in index order so this
            # simple insert should work fine
            added = diff.get_added()
            for indexed_row in added:
                self._row_list.insert(indexed_row.index, self._create_row(indexed_row.row))
            # get the moved rows from the new list of rows
            moved_indices = diff.get_moved(tuple(row.get_row() for row in self._row_list))
            # reverse sort the moved_indices by current_index so that they can be popped
            reversed_moved_indices = sorted(moved_indices, key=lambda moved_index: moved_index[0], reverse=True)
            moved_rows = tuple((next_index, self._row_list.pop(current_index))
                               for current_index, next_index in reversed_moved_indices)
            # sort the moved rows by the next_index so that they can be inserted
            sorted_moved_rows = sorted(moved_rows, key=lambda moved_row: moved_row[0])
            for (next_index, row) in sorted_moved_rows:
                self._row_list.insert(next_index, row)
            # if anything was added then focus the last added index
            # else focus the previously focused item
            if len(added) > 0:
                self._row_list.focus = added[len(added) - 1].index
            else:
                if focused is not None:
                    self._row_list.focus = self._row_list.index(focused)
            # cache the new rows data
            self._rows = rows
