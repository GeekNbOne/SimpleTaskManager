from multiprocessing import Process
from abc import abstractmethod
import uuid
from enum import Enum

class MessageType(Enum):
    StatusUpdate = 1
    RaiseIssue = 2
    TaskDone = 3


class Task(Process):

    def __init__(self, message_queue, *args, **kwargs):
        super(Task, self).__init__()
        self._args = args
        self._kwargs = kwargs
        self._message_queue = message_queue

        self._id = uuid.uuid4()

    @property
    def id(self):
        return self._id

    def raise_issue(self, severity, message, diagnostic):
        self._message_queue.put((self.id,MessageType.RaiseIssue, severity, message, diagnostic))

    def update_status(self, msg):
        self._message_queue.put((self.id,MessageType.StatusUpdate, msg))

    def run(self) -> None:
        try:
            self.target(*self._args, **self._kwargs)
        except Exception as e:
            print(e)

        self._message_queue.put((self.id,MessageType.TaskDone))

    @abstractmethod
    def target(self, *args, **kwargs):
        pass
