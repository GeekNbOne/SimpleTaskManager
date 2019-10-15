from datetime import datetime
from .completed_task import CompletedTask

INITIAL_STATUS = 'Task just started'


class RunningTask(object):

    def __init__(self, ref, tags =None, initial_status=INITIAL_STATUS):
        self._start_time = datetime.now()
        self._ref = ref
        if tags is None:
            self._tags = {}
        else:
            self._tags = tags
        self._issues = []
        self.status = initial_status


    def __hash__(self):
        return hash((self._ref.task_name,self._tags))

    @property
    def tags(self):
        return self._tags

    @property
    def ref(self):
        return self._ref

    @property
    def issues(self):
        return self._issues

    @property
    def start_time(self):
        return self._start_time

    @property
    def type(self):
        return self.ref.__class__.__name__


    @property
    def running_time(self):
        return datetime.now() - self._start_time

    def complete(self,error= None,traceback = None):
        ct =  CompletedTask(self._ref.name,self._ref.__class__.__name__,self.tags,self.issues,self._start_time,datetime.now())
        if error is not None:
            ct.set_error(error,traceback)

        return ct
