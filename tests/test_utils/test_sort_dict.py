from collections import OrderedDict

from pytest import fixture

from django_ontruck.utils.sort_dict import sort_dict


@fixture
def dict_to_sort():
    return {
        'B': 2,
        'A': {
            'D': 4,
            'C': {
                'F': 6,
                'E': 5,
            },
        }
    }


@fixture
def sorted_dict():
    return OrderedDict((
        (
            'A',
            OrderedDict(
                (
                    ('C', OrderedDict((('E', 5), ('F', 6)))),
                    ('D', 4)
                )
            )
        ),
        ('B', 2,)
    ))


def test_it_sorts_the_dict_in_alphabetical_order_of_keys(
    dict_to_sort, sorted_dict
):
    assert sort_dict(dict_to_sort) == sorted_dict


def test_sorts_empty_dicts():
    assert sort_dict({}) == OrderedDict()
