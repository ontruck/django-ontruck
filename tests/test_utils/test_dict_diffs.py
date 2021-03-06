from collections import OrderedDict
from textwrap import dedent

from pytest import fixture, mark

from django_ontruck.utils.diff_dicts import (
    Modification, Deletion, Addition, diff_dicts, DictDiff, KeyPath, missing
)


@fixture
def left():
    return {
        'a': {
            'b': {
                'c': 1,
                'd': 2
            },
            'e': 3,
        },
        'f': 4,
        'i': [
            7
        ],
        'j': [
            'ABCDEF'
        ],
    }


@fixture
def right():
    return {
        'a': {
            'e': 3,
            'b': {
                'c': 11,
            },
        },
        'f': {
            'h': 6
        },
        'g': 5,
        'i': [
            8, 9
        ],
        'j': [
            'XYZ'
        ]
    }


def test_diff_dict(left, right):
    assert diff_dicts(left, right) == DictDiff(
        OrderedDict(
            [
                (
                    'a',
                    DictDiff(
                        OrderedDict(
                            [
                                (
                                    'b',
                                    DictDiff(
                                        OrderedDict(
                                            [
                                                ('c', Modification(1, 11)),
                                                ('d', Deletion(2))
                                            ]
                                        )
                                    )
                                ),
                            ]
                        )
                    )
                ),
                ('f', Modification(4, {'h': 6})),
                ('g', Addition(5)),
                (
                    'i',
                    DictDiff(
                        OrderedDict(
                            [
                                (0, Modification(7, 8)),
                                (1, Addition(9))
                            ]
                        )
                    )
                ),
                (
                    'j',
                    DictDiff(
                        OrderedDict(
                            [
                                (0, Modification('ABCDEF', 'XYZ'))
                            ]
                        )
                    )
                ),
            ]
        )
    )


def test_when_the_same(left):
    assert diff_dicts(left, left) == DictDiff.empty()


def test_empty_diffs_are_falsey():
    assert not DictDiff.empty()


def test_non_empty_diffs_are_truthy(left, right):
    assert diff_dicts(left, right)


def test_iteration(left, right):
    assert list(diff_dicts(left, right)) == [
        (KeyPath('a', 'b', 'c'), Modification(1, 11)),
        (KeyPath('a', 'b', 'd'), Deletion(2)),
        (KeyPath('f'), Modification(4, {'h': 6})),
        (KeyPath('g'), Addition(5)),
        (KeyPath('i', 0), Modification(7, 8)),
        (KeyPath('i', 1), Addition(9)),
        (KeyPath('j', 0), Modification('ABCDEF', 'XYZ'))
    ]


def test_len(left, right):
    assert len(diff_dicts(left, right)) == 7


def test_key_lookup(left, right):
    diff = diff_dicts(left, right)

    assert diff['a']['b']['c'] == Modification(1, 11)
    assert diff['a']['b']['d'] == Deletion(2)
    assert diff['f'] == Modification(4, {'h': 6})
    assert diff['g'] == Addition(5)
    assert diff['i'][0] == Modification(7, 8)
    assert diff['i'][1] == Addition(9)
    assert diff['j'][0] == Modification('ABCDEF', 'XYZ')


def test_str(left, right):
    assert (
        str(diff_dicts(left, right)) == dedent(
        f'''
            [ * ] /a/b/c : left: 1 | right: 11
            [ - ] /a/b/d : left: 2 | right:{' '}
            [ * ] /f : left: 4 | right: {{'h': 6}}
            [ + ] /g : left:  | right: 5
            [ * ] /i/0 : left: 7 | right: 8
            [ + ] /i/1 : left:  | right: 9
            [ * ] /j/0 : left: ABCDEF | right: XYZ
            '''
    ).strip()
    )


@mark.parametrize(
    ('diff',),
    (
        (Modification(1, 2),),
        (Addition(1),),
        (Deletion(1),),
    )
)
def test_scalar_diffs_are_hashable(diff):
    assert hash(diff)


def test_left(left, right):
    assert diff_dicts(left, right).left == OrderedDict(
        [
            (
                'a', OrderedDict(
                    [
                        (
                            'b',
                            OrderedDict([('c', 1), ('d', 2)])
                        )
                    ]
                )
            ),
            ('f', 4),
            ('g', missing),
            (
                'i',
                OrderedDict([(0, 7), (1, missing)])
            ),
            (
                'j',
                OrderedDict([(0, 'ABCDEF')])
            )
        ]
    )


def test_right(left, right):
    assert diff_dicts(left, right).right == OrderedDict(
        [
            (
                'a',
                OrderedDict(
                    [
                        (
                            'b',
                            OrderedDict(
                                [
                                    ('c', 11),
                                    ('d', missing)
                                ]
                            )
                        )
                    ]
                )
            ),
            ('f', {'h': 6}),
            ('g', 5),
            ('i', OrderedDict([(0, 8), (1, 9)])),
            ('j', OrderedDict([(0, 'XYZ')]))
        ]
    )
