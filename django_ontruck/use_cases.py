from abc import ABCMeta, abstractmethod

from django.db import transaction


class UseCaseBase:
    __metaclass__ = ABCMeta

    def __init__(self, disable_events=False):
        self.events = []
        self.disable_events = disable_events

    def execute(self, command, executed_by=None):
        with transaction.atomic():
            response_in_commit = self.execute_in_commit(command, executed_by)
            transaction.on_commit(lambda: self.execute_post_commit())
        return response_in_commit

    @abstractmethod
    def execute_in_commit(self, command, executed_by=None):
        raise NotImplementedError

    def execute_post_commit(self):
        if not self.disable_events:
            for event in self.events:
                event.send()
