import urwid

COLUMN_WEIGHTS = [2, 1, 1]


def get_field(fields, index):
    try:
        return fields[index]
    except IndexError:
        return BlankField()


def column_tuple(fields, index):
    return 'weight', COLUMN_WEIGHTS[index], get_field(fields, index)


class BlankField(urwid.Text):
    def __init__(self):
        super().__init__(u'')


class ColumnLabel(urwid.Columns):
    def __init__(self, text):
        super().__init__([
            (2, urwid.Text(u'| ')),
            urwid.Text(text),
            (2, urwid.Text(u' |')),
        ])


class Field(urwid.WidgetWrap):
    def __init__(self, text):
        super().__init__(
            urwid.AttrMap(urwid.Button(text),
                          None, focus_map='reversed')
        )


class ColumnLayout(urwid.Columns):
    def __init__(self, fields):
        super().__init__([
            column_tuple(fields, 0),
            column_tuple(fields, 1),
            column_tuple(fields, 2),
        ])


class Row(ColumnLayout):
    def __init__(self, index):
        super().__init__([
            Field(u'row %s - column 1' % index),
            Field(u'row %s - column 2' % index),
            Field(u'row %s - column 3' % index),
        ])


class Table(urwid.ListBox):
    def __init__(self):
        super().__init__(urwid.SimpleFocusListWalker([
            Row(0),
            Row(1),
            Row(2),
            Row(3),
            Row(4),
            Row(5),
            Row(6),
            Row(7),
            Row(8),
            Row(9),
            Row(10),
            Row(11),
            Row(12),
            Row(13),
            Row(14),
            Row(15),
            Row(16),
            Row(17),
            Row(18),
            Row(19),
            Row(20),
            Row(21),
            Row(22),
            Row(23),
            Row(24),
            Row(25),
            Row(26),
            Row(27),
            Row(28),
            Row(29),
            Row(30),
            Row(31),
            Row(32),
        ]))


class ColumnLabels(ColumnLayout):
    def __init__(self):
        super().__init__([
            ColumnLabel(u'column 1'),
            ColumnLabel(u'column 2'),
            ColumnLabel(u'column 3'),
        ])


class Header(urwid.Pile):
    def __init__(self):
        super().__init__([
            ColumnLabels(),
            urwid.Divider(u'-'),
        ])


class Instructions(urwid.Text):
    def __init__(self):
        super().__init__(u'q - exit')


class Footer(urwid.Pile):
    def __init__(self):
        super().__init__([
            urwid.Divider(u'-'),
            Instructions(),
        ])


class Layout(urwid.Frame):
    def __init__(self):
        super().__init__(
            Table(),
            Header(),
            Footer()
        )
