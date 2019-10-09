from abc import ABC, abstractmethod
from .completed_task import CompletedTask


class TaskObserver(ABC):

    @abstractmethod
    def task_finished(self, task: CompletedTask):
        pass
