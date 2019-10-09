from multiprocessing import Process
from abc import abstractmethod
import uuid
from enum import Enum
from datetime import datetime
import traceback

class MessageType(Enum):
    StatusUpdate = 1
    RaiseIssue = 2
    TaskSuccessful = 3
    TaskError = 4


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
        self._start_time = datetime.now()
        try:
            self.target(*self._args, **self._kwargs)
        except Exception as e:
            self._message_queue.put((self.id,MessageType.TaskError,f'{e.__class__.__name__}: {str(e)}',traceback.format_exc()))
        else:
            self._message_queue.put((self.id,MessageType.TaskSuccessful))

    @abstractmethod
    def target(self, *args, **kwargs):
        pass

    @property
    def start_time(self):
        return getattr(self,'_start_time',None)

