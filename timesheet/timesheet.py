import datetime

class Interval(object):
    def __init__(self, start, end, date, project, task):
        self.start = start
        self.end = end
        self.date = date
        self.project = project
        self.task = task


class Timesheet(object):
    def __init__(self):
        self.tasks = []

    def time_spent(self):
        return 0

    def add_time(self, start, end=None, task=None, proj=None, date=None):
        ''' Add time to the timesheet. If the interval overlaps any other
            interval, raise ValueError unless force = True.

            start - Start time, either HH:MM AM (or PM), or object with 
                    .hour and .minute properties.

            end   - (optional) Same as start. If None (default) then this
                    task will be marked as the current_task. If there is a
                    current_task already, its end will be set to now.

            task  - (optional) The task you've been working on.

            date  - (optional) The date, either YYYY-MM-DD, or an object with
                    .year, .month, and .day properties. If no date is 
                    provided, the current date will be used.

        '''

        try:
            start = datetime.time(start.hour, start.minute)
        except AttributeError:
            # Maybe it's a string?
            start = datetime.datetime.strptime(start, "%I:%M %p")


        _task = self.current_task
        if _task is not None:
            _task.end = datetime.datetime.today().time()

        if end is not None:
            try:
                end = datetime.time(end.hour, end.minute)
            except AttributeError:
                # Maybe it's a string?
                end = datetime.datetime.strptime(end, "%I:%M %p")

        if date is None:
            date = datetime.date.today()
        else:
            try:
                date = datetime.date(date.year, date.month, date.day)
            except AttributeError:
                date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        task = Interval(start, end, date, proj, task)
        self.tasks.append(task)


    @property
    def current_task(self):
        for task in self.tasks:
            if task.end is None:
                return task
        
        return None
