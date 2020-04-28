from django_ontruck.use_cases import UseCaseBase

from .events import FooEvent
from .models import FooModel


class FooCreateUseCase(UseCaseBase):

    def execute_in_commit(self, command, executed_by=None):
        example = FooModel.objects.create(**command)
        self.events.append(FooEvent(attr1='attr1_value'))
        return example


class FooUpdateUseCase(UseCaseBase):

    def execute_in_commit(self, command, executed_by=None):
        id = command.pop('id')
        example = FooModel.objects.get(id=id)
        for key, value in command.items():
            setattr(example, key, value)
        example.save()
        self.events.append(FooEvent(attr1='attr1_value'))
        return example
