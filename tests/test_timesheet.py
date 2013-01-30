from timesheet import Timesheet
import unittest

class GivenNewTimesheet(unittest.TestCase):

    def setUp(self):
        self.timesheet = Timesheet()
        

    def test_it_should_have_no_time_spent(self):
        self.assertEqual(0, self.timesheet.time_spent())


    def test_adding_time_with_no_parameters_should_TypeError(self):
        with self.assertRaises(TypeError):
            self.timesheet.add_time()


    def test_adding_time_with_bad_format_should_ValueError(self):
        with self.assertRaises(ValueError):
            self.timesheet.add_time("1234")


    def test_adding_time_with_HH_MM_SS_AM_should_not_ValueError(self):
        self.timesheet.add_time("12:42 AM")


class GivenTimesheetWithOneInterval(unittest.TestCase):

    def setUp(self):
        self.timesheet = Timesheet()
        self.timesheet.add_time()
