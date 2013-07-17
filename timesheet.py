import datetime

class Timesheet:
    def __init__(self):
        self.projects = {}
        self.tasks = []
        self.intervals = []
        self._current_task = None


    @property
    def current_task(self):
        return self._current_task


    def new_project(self, proj_id, title=None, desc=None):
        self.projects[proj_id] = Project(proj_id, title, desc)


    def add_project(self, proj):
        if self.projects.get(proj.id) is None:
            self.projects[proj.id] = proj
        else:
            raise ValueError("Cannot add two projects with id {}".format(proj.id))


    def get_project(self, proj_id):
        return self.projects.get(proj_id)


    def new_task(self, title=None, proj_id=None, type=None, reporter=None,
                 owner=None):
        max_id = self.tasks[-1].id if self.tasks else 0
        task = Task(max_id+1, 
                    title=title,
                    proj_id=proj_id,
                    type=type,
                    reporter=reporter,
                    owner=owner)
        self.tasks.append(task)
        return task.id


    def get_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    
    def add_work(self, task_id, start, end=None):
        task = self.get_task(task_id)
        if task is None:
            raise ValueError("No task present with id '{}'".format(task_id))
        self.intervals.append(Interval(task_id, start, end))


    def start_work(self, task_id):
        task = self.get_task(task_id)
        if task is None:
            raise ValueError("No task present with id '{}'".format(task_id))
        self._current_task = task


    def stop_work(self):
        self._current_task = None


class Project:
    def __init__(self, id=None, title=None, desc=None):
        self.id = id
        self.title = title
        self.desc = desc


class Task:
    def __init__(self, id, title=None, proj_id=None, type=None, reporter=None,
                 owner=None):
        self._id = id
        self.title = title
        self.proj_id = proj_id
        self.type = type
        self.reporter = reporter
        self.owner = owner

    @property
    def id(self):
        return self._id


class Note:
    def __init__(self, task_id, tstamp, text):
        pass


class Interval:
    def __init__(self, task_id, start, end=None):
        self.task_id = task_id
        self.start = start
        self.end = end
        if self.end is not None:
            try:
                self.end - self.start
            except TypeError:
                raise ValueError("start and end types are not compatible.")


    @property
    def time_spent(self):
        if self.end is None:
            end = datetime.datetime.now()
        else:
            end = self.end

        return end - self.start

