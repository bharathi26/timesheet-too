from datetime import datetime


class Timesheet(object):
    def time_spent(self):
        return 0

    def add_time(self, start):
        start = datetime.strptime(start, "%I:%M %p")
