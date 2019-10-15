from multiprocessing import Process
from abc import abstractmethod
import uuid
from enum import Enum
import traceback


class MessageType(Enum):
    StatusUpdate = 1
    RaiseIssue = 2
    TaskSuccessful = 3
    TaskError = 4


class Task(Process):

    def __init__(self, message_queue, run_queue, *args, **kwargs):
        super(Task, self).__init__()
        self._args = args
        self._kwargs = kwargs
        self._message_queue = message_queue
        self._run_queue = run_queue

        self._id = uuid.uuid4()

    @property
    def id(self):
        return self._id

    def raise_issue(self, severity, tags, message, diagnostic):
        self._message_queue.put((self.id, MessageType.RaiseIssue, severity, tags, message, diagnostic))

    def update_status(self, msg):
        self._message_queue.put((self.id, MessageType.StatusUpdate, msg))

    def launch_task(self, task, tags, *args):
        self._run_queue.put((task, tags, args))

    def run(self) -> None:
        try:
            self.target(*self._args, **self._kwargs)
        except Exception as e:
            self._message_queue.put(
                (self.id, MessageType.TaskError, f'{e.__class__.__name__}: {str(e)}', traceback.format_exc()))
        else:
            self._message_queue.put((self.id, MessageType.TaskSuccessful))

    @abstractmethod
    def target(self, *args, **kwargs):
        pass

    @classmethod
    @property
    def task_name(cls):
        return cls.__name__
