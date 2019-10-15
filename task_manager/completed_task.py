class CompletedTask(object):

    def __init__(self, name,type,tags, issues, start_time, end_time):
        self._name = name
        self._type = type
        self._error = None
        self._issues = issues
        self._start_time = start_time
        self._end_time = end_time
        self._tags = tags

    def set_error(self, message, traceback):
        self._error = {'message': message, 'traceback': traceback}

    @property
    def name(self):
        return self._name

    @property
    def successful(self):
        return self._error is None

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def issues(self):
        return self._issues

    @property
    def error(self):
        return self._error

    @property
    def tags(self):
        return self._tags

    @property
    def type(self):
        return self._type

    def __repr__(self):
        if self.successful:
            return f'<Successful task {self._name}: {len(self.issues)} issues>'
        else:
            return f'<Error in task {self._name}: {self._error["message"]}>'

