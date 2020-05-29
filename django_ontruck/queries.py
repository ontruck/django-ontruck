from abc import ABCMeta, abstractmethod


class QueryBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, command, executed_by=None):
        raise NotImplementedError
