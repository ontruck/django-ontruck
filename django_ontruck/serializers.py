import json
from collections import OrderedDict

from rest_framework.fields import JSONField


class DictSort:
    def __init__(self, sort_method):
        self.sort_method = sort_method
        self._queue = []

    def _items(self):
        while True:
            if self._queue:
                yield self._queue.pop(0)
            else:
                return

    def _enqueue(self, dict_to_sort, current):
        for key in self.sort_method(dict_to_sort):
            self._queue.append((key, dict_to_sort[key], current))

    def _handle_item(self, key, value, current):
        if not isinstance(value, dict):
            current[key] = value

            return

        current[key] = OrderedDict()

        self._enqueue(value, current[key])

    def __call__(self, dict_to_sort):
        sorted_dict = OrderedDict()

        self._enqueue(dict_to_sort, sorted_dict)

        for key, value, current in self._items():
            self._handle_item(key, value, current)

        return sorted_dict


class SortedJSONField(JSONField):
    def __init__(self, *args, **kwargs):
        self.sort_method = kwargs.pop('sort_method', sorted)

        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        representation = super().to_representation(value)

        if self.binary:
            if isinstance(representation, bytes):
                representation = representation.decode('utf-8')

            return json.dumps(json.loads(representation), sort_keys=True)

        return DictSort(self.sort_method)(representation)
