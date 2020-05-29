from django_ontruck.queries import QueryBase

from .events import FooEvent
from .models import FooModel


class CountFooQuery(QueryBase):

    def execute(self, command, executed_by=None):
        text = command.get('title')
        return {'count': FooModel.objects.filter(title__contains=text).count()}
