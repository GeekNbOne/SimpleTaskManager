from multiprocessing import Queue, RLock, Process
from threading import Thread
import copy
from .task import MessageType


class Listener(Thread):

    def __init__(self, handle, q):
        self._q = q
        self._handle = handle
        super(Listener, self).__init__()

    def run(self) -> None:
        while True:
            self._handle(*self._q.get())


class TaskManager(object):

    def __init__(self):
        self._r_lock = RLock()
        self._tasks = {}

        self._message_queue = Queue()

        self._start_listener(self.process_message, self._message_queue)

    def process_message(self, task_id, message_type, *args):
        mt_map = {MessageType.StatusUpdate: self.update_status,
                  MessageType.RaiseIssue: self.raise_issue,
                  MessageType.TaskDone: self.task_finish}

        mt_map[message_type](task_id, *args)

    def update_status(self, task_id, message):
        with self._r_lock:
            self._tasks[task_id]['status'] = message

    def task_finish(self, task_id):
        with self._r_lock:
            task = self._tasks[task_id]['ref']
            task.join()
            del self._tasks[task_id]

    def raise_issue(self, task_id, severity, message, diagnostic):
        self._tasks[task_id]['issues'].append((severity, message, diagnostic))

    def run_task(self, task, *args, **kwargs):
        t = task(self._message_queue, *args, **kwargs)
        self._tasks[t.id] = {'ref': t, 'status': 'Just started', 'issues': []}
        t.start()

    @property
    def tasks(self):
        with self._r_lock:
            return copy.copy(self._tasks)

    def _start_listener(self, handle, queue):
        l = Listener(handle, queue)
        l.daemon = True
        l.start()

    @property
    def is_running(self):
        return len(self._tasks) > 0
