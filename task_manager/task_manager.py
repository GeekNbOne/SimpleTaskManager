from multiprocessing import Queue, RLock
from threading import Thread
import copy
from .task import MessageType
from .task_observer import TaskObserver
from .completed_task import CompletedTask
from datetime import datetime


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
        self._obs_lock = RLock()
        self._tasks = {}
        self._observers = []

        self._message_queue = Queue()

        self._start_listener(self._process_message, self._message_queue)

    def add_observer(self, observer: TaskObserver):
        with self._obs_lock:
            self._observers.append(observer)

    def remove_observer(self, observer: TaskObserver):
        with self._obs_lock:
            self._observers.remove(observer)

    def run_task(self, task, tags=None, *args, **kwargs):
        if tags is None:
            tags = {}

        t = task(self._message_queue, *args, **kwargs)
        self._tasks[t.id] = {'ref': t, 'status': 'Just started', 'issues': [], 'tags': tags}
        t.start()

    @property
    def tasks(self):
        with self._r_lock:
            return copy.copy(self._tasks)

    def get_task(self,task_id):
        with self._r_lock:
            return self._tasks[task_id]

    @property
    def is_running(self):
        return len(self._tasks) > 0

    def _process_message(self, task_id, message_type, *args):
        mt_map = {MessageType.StatusUpdate: self._update_status,
                  MessageType.RaiseIssue: self._raise_issue,
                  MessageType.TaskSuccessful: self._task_successful,
                  MessageType.TaskError: self._task_error}

        mt_map[message_type](task_id, *args)

    def _start_listener(self, handle, queue):
        l = Listener(handle, queue)
        l.daemon = True
        l.start()

    def _notify_observer(self, completed_task: CompletedTask):
        with self._obs_lock:
            for observer in self._observers:
                observer.task_finished(completed_task)

    def _update_status(self, task_id, message):
        with self._r_lock:
            self._tasks[task_id]['status'] = message

    def _task_error(self, task_id, message, traceback):

        def set_error(completed_task):
            completed_task.set_error(message, traceback)

        self._end_task(task_id, set_error)

    def _task_successful(self, task_id):

        self._end_task(task_id)

    def _get_completed_task(self, reg_task):
        task = reg_task['ref']
        return CompletedTask(task.__class__.__name__, reg_task['tags'], reg_task['issues'],task.start_time, datetime.now())

    def _end_task(self, task_id, handle=None):
        reg_task = self.get_task(task_id)
        task = reg_task['ref']

        completed_task = self._get_completed_task(reg_task)
        if handle is not None:
            handle(completed_task)

        self._notify_observer(completed_task)
        with self._r_lock:
            task.join()
            del self._tasks[task.id]

    def _raise_issue(self, task_id, severity, message, diagnostic):
        self._tasks[task_id]['issues'].append((severity, message, diagnostic))
