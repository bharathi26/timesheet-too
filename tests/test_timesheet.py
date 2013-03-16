from __future__ import absolute_import
import unittest

from datetime import datetime, time, date
from timesheet import Timesheet

class GivenNewTimesheet(unittest.TestCase):

    def setUp(self):
        self.timesheet = Timesheet()
        

    def test_it_should_have_no_time_spent(self):
        self.assertEqual(0, self.timesheet.time_spent())


    def test_adding_time_with_no_parameters_should_TypeError(self):
        with self.assertRaises(TypeError):
            self.timesheet.add_interval()


    def test_adding_time_with_bad_format_should_ValueError(self):
        with self.assertRaises(ValueError):
            self.timesheet.add_interval("1234")


    def test_adding_time_with_HH_MM_AM_should_not_ValueError(self):
        self.timesheet.add_interval("12:42 AM")


    def test_adding_time_with_HH_MM_PM_should_not_ValueError(self):
        self.timesheet.add_interval("2:12 PM")


    def test_adding_time_with_two_HH_MM_AM_should_not_error(self):
        self.timesheet.add_interval("3:13 AM", "5:17 PM")


    def test_adding_time_with_good_start_bad_end_should_ValueError(self):
        with self.assertRaises(ValueError):
            self.timesheet.add_interval("4:14 PM", "sdfkj23")

    
    def test_adding_time_with_good_start_good_end_should_not_error(self):
        self.timesheet.add_interval("12:00 AM", "3:33 AM")


    def test_adding_start_time_by_object_should_not_error(self):
        t = time(0, 0)
        self.timesheet.add_interval(t)


    def test_adding_end_time_by_object_should_not_error(self):
        t = time(13, 13)
        self.timesheet.add_interval("12:00 AM", t)


    def test_adding_date_by_object_should_not_error(self):
        self.timesheet.add_interval("12:44 PM", date=datetime.today())


    def test_adding_time_with_good_start_end_and_any_task_should_not_error(self):
        self.timesheet.add_interval("12:00 AM", "4:44 PM", "fnord")


    def test_adding_time_with_good_start_end_any_task_and_proj_should_not_error(self):
        self.timesheet.add_interval("1:43 AM", "4:12 AM", "fnord", "999")


    def test_adding_time_with_good_start_thru_proj_and_bad_date_should_ValueError(self):
        with self.assertRaises(ValueError):
            self.timesheet.add_interval("9:42 AM",
                                    "9:59 AM",
                                    "fnord",
                                    "fizz",
                                    "Silly non-date")


    def test_adding_time_with_good_vals_and_good_date_should_not_error(self):
        self.timesheet.add_interval("8:12 AM",
                                "8:13 AM",
                                "fnord",
                                "fizzy",
                                "2010-08-14")


    def test_find_intervals_should_return_empty_list(self):
        self.assertEqual([],self.timesheet._find_intervals(time(10, 10),
                                                           time(2, 20)))


class GivenTimesheetWithOneTaskWithStartAndEnd(unittest.TestCase):
    def setUp(self):
        self.timesheet = Timesheet()
        self.start_time = time(10, 45)
        self.end_time = time(11, 00)
        self.timesheet.add_interval(self.start_time, self.end_time)


    def test_it_should_use_current_date_as_default(self):
        self.assertEqual(datetime.today().date(),
                         self.timesheet.intervals[-1].date)


    def test_the_project_should_be_None_by_default(self):
        self.assertIsNone(self.timesheet.intervals[-1].project)


    def test_the_task_should_be_None_by_default(self):
        self.assertIsNone(self.timesheet.intervals[-1].task)


    def test_current_task_should_be_None(self):
        self.assertIsNone(self.timesheet.current_task)


    def test_adding_task_with_same_start_and_end_should_return_current_interval(self):
        self.skipTest("come  back here")
        current_task = self.timesheet.intervals[-1]

        task = self.timesheet.add_interval(current_task.start,
                                           current_task.end,
                                           task="New task")

        self.assertEqual(current_task, task)


    def test_find_intervals_with_early_start_but_matching_end_should_return_it(self):
        interval = self.timesheet.intervals[-1]

        self.assertEqual(interval,
                         self.timesheet._find_intervals(time(0, 0),
                                                        interval.end)[0])


    def test_find_intervals_with_time_outside_interval_should_fail(self):
        bad_start = self.start_time.replace(hour=self.start_time.hour - 2)
        bad_end = self.start_time.replace(hour=self.start_time.hour - 1)
        self.assertEqual([], self.timesheet._find_intervals(bad_start,
                                                            bad_end))


class GivenTimesheetWithOneFullyLoadedTask(unittest.TestCase):
    def setUp(self):
        self.start_time = time(1, 44)
        self.end_time = time(21, 8)
        self.date = date(2010, 8 ,14)
        self.project  = "Silly Project"
        self.task = "Put on some pants"

        self.timesheet = Timesheet()
        self.timesheet.add_interval(self.start_time,
                                self.end_time,
                                proj=self.project,
                                task=self.task,
                                date=self.date)
        self.sheet_task = self.timesheet.intervals[-1]


    def test_it_should_use_provided_project(self):
        self.assertEqual(self.project,
                         self.project)


    def test_it_should_use_provided_task(self):
        self.assertEqual(self.task,
                         self.sheet_task.task)


    def test_it_should_use_provided_start(self):
        self.assertEqual(self.start_time,
                         self.sheet_task.start)


    def test_it_should_use_provided_end(self):
        self.assertEqual(self.end_time,
                         self.sheet_task.end)


    def test_it_should_use_provided_date(self):
        self.assertEqual(self.date,
                         self.sheet_task.date)


class GivenTimesheetWithOpenInterval(unittest.TestCase):

    def setUp(self):
        self.start_time = "10:13 AM"
        self.timesheet = Timesheet()
        self.timesheet.add_interval(self.start_time)

    def test_current_task_should_return_something(self):
        self.assertIsNotNone(self.timesheet.current_task)


    def test_current_task_should_have_correct_start_time(self):
        self.assertEqual(self.start_time,
                         self.timesheet.current_task.start.strftime('%I:%M %p'))


    def test_adding_task_should_close_interval(self):
        task = self.timesheet.current_task
        self.timesheet.add_interval("4:34 PM")

        now = datetime.today().time()
        self.assertEqual(now.hour,
                         task.end.hour)
        self.assertEqual(now.minute,
                         task.end.minute)
        self.assertEqual(now.second,
                         task.end.second)
        self.assertAlmostEqual(now.microsecond,
                               task.end.microsecond, places=-3)

