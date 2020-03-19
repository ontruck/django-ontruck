from django_ontruck.use_cases import UseCaseBase

from .events import FooEvent
from .models import FooModel

class FooUseCase(UseCaseBase):

    def execute_in_commit(self, command, executed_by=None):
        example = FooModel.objects.create(**command)
        self.events.append(FooEvent(attr1='attr1_value'))
        return example
