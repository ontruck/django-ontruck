import json
from collections import OrderedDict

from pytest import fixture

from django_ontruck.serializers import DictSort, SortedJSONField


class TestSerializers:
    @fixture
    def dict_to_sort(self):
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
    def sorted_dict(self):
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

    class TestDictSort:
        @fixture
        def dict_sort(self):
            return DictSort(sort_method=sorted)

        def test_it_sorts_the_dict_in_alphabetical_order_of_keys(
            self, dict_to_sort, dict_sort, sorted_dict
        ):
            assert dict_sort(dict_to_sort) == sorted_dict

    class TestSortedJSONField:
        @fixture
        def binary(self):
            return False

        @fixture
        def sorted_json_field(self, binary):
            return SortedJSONField(binary=binary)

        def test_it_sorts_the_dict_in_alphabetical_order_of_keys(
            self, dict_to_sort, sorted_json_field, sorted_dict
        ):
            assert (
                sorted_json_field.to_representation(dict_to_sort) ==
                sorted_dict
            )

        class TestWhenBinaryIsTrue:
            @fixture
            def binary(self):
                return True

            def test_it_sorts_the_dict_in_alphabetical_order_of_keys(
                self, dict_to_sort, sorted_json_field, sorted_dict
            ):
                assert (
                    sorted_json_field.to_representation(dict_to_sort) ==
                    json.dumps(sorted_dict)
                )
