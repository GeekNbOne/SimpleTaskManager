from multiprocessing import Queue, RLock
from threading import Thread
import copy
from .task import MessageType
from .task_observer import TaskObserver
from .completed_task import CompletedTask
from .running_task import RunningTask


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
        self._running_tasks = {}
        self._observers = []

        self._message_queue = Queue()
        self._run_queue = Queue()

        self._start_listener(self._process_message, self._message_queue)
        self._start_listener(self.run_task, self._run_queue)

    def add_observer(self, observer: TaskObserver):
        with self._obs_lock:
            self._observers.append(observer)

    def remove_observer(self, observer: TaskObserver):
        with self._obs_lock:
            self._observers.remove(observer)

    def run_task(self, task, tags=None, *args, **kwargs):
        with self._r_lock:
            t = task(self._message_queue, self._run_queue, *args, **kwargs)
            self._running_tasks[t.id] = RunningTask(t, tags)
            t.start()


    @property
    def running_tasks(self):
        with self._r_lock:
            return copy.copy(self._running_tasks)

    def get_running_task(self, task_id):
        with self._r_lock:
            return self._running_tasks[task_id]

    @property
    def is_running(self):
        return len(self._running_tasks) > 0

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
            self._running_tasks[task_id].status = message

    def _task_error(self, task_id, message, traceback):
        self._end_task(task_id, message, traceback)

    def _task_successful(self, task_id):
        self._end_task(task_id)

    def _end_task(self, task_id, error=None, traceback=None):
        task = self.get_running_task(task_id)

        completed_task = task.complete(error, traceback)

        self._notify_observer(completed_task)

        with self._r_lock:
            task.ref.join()
            del self._running_tasks[task_id]

    def _raise_issue(self, task_id, severity, tags, message, diagnostic):
        if tags is None:
            tags = {}

        self._running_tasks[task_id].issues.append((severity, tags, message, diagnostic))
