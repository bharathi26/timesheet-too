import datetime

class Task(object):
    def __init__(self, start, end, date):
        self.start = start
        self.end = end
        self.date = date

class Timesheet(object):
    def __init__(self):
        self.tasks = []

    def time_spent(self):
        return 0

    def add_time(self, start, end=None, task=None, proj=None, date=None):
        start = datetime.datetime.strptime(start, "%I:%M %p")
        if end is not None:
            end = datetime.datetime.strptime(end, "%I:%M %p")
        if date is None:
            date = datetime.date.today()
        else:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        task = Task(start, end, date)
        self.tasks.append(task)


    @property
    def current_task(self):
        for task in self.tasks:
            if task.end is None:
                return task
        
        return None
