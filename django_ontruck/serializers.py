import json
from rest_framework.fields import JSONField

from django_ontruck.utils.sort_dict import sort_dict


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

        return sort_dict(representation, sort_method=self.sort_method)
