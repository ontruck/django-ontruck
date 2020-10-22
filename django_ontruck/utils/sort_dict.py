from collections import OrderedDict


class SortDict:
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


def sort_dict(dict_, sort_method=sorted):
    return SortDict(sort_method)(dict_)
