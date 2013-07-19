import logging
import pytest
import datetime
import time
from timesheet import *
logging.basicConfig(filename='time.log', level=logging.DEBUG)
log = logging


@pytest.fixture
def timesheet():
    return Timesheet()


def assume(value, msg=''):
    if not value:
        pytest.skip(msg)


#Interval tests
def test_Interval_with_no_task_id_should_TypeError():
    with pytest.raises(TypeError):
        Interval()


def test_Interval_with_no_start_should_TypeError():
    with pytest.raises(TypeError):
        Interval(42)


def test_Interval_with_task_id_and_start_should_work():
    Interval(3, datetime.datetime.now())


def test_if_end_provided_and_cannot_subtract_start_it_should_ValueError():
    with pytest.raises(ValueError):
        i = Interval(3, 42, 'Hello')


def test_Interval_with_task_id_should_have_it_set():
    i = Interval(3, 42)
    assert i.task_id == 3


def test_Interval_with_start_should_have_it_set():
    i = Interval(3, 42)
    assert i.start == 42


def test_Interval_with_end_should_have_it_set():
    i = Interval(3, 42, 16)
    assert i.end == 16


def test_if_end_not_provided_time_spent_should_return_now_minus_start():
    start = datetime.datetime.now()
    i = Interval(3, start)
    time.sleep(0.3)

    spent = i.time_spent
    also_spent = datetime.datetime.now() - start
    diff = also_spent.total_seconds()/60/60 - spent

    assert abs(diff) < .001 # Within .0001 seconds


def test_if_end_provided_time_spent_should_equal_end_minus_start():
    start = datetime.datetime(1984, 8, 26, 8, 43)
    end = datetime.datetime.now()
    i = Interval(3, start, end)

    assert i.time_spent == (end-start).total_seconds()/60/60


#Task tests
def test_task_id_should_be_required_on_creation():
    with pytest.raises(TypeError):
        Task()


def test_task_id_should_be_immutable_on_creation():
    task = Task(42)
    with pytest.raises(AttributeError):
        task.id = 3


def test_task_id_should_be_value_passed_in_constructor():
    task = Task(42)
    assert task.id == 42


def test_task_title_should_be_none_if_not_passed_in():
    task = Task(42)
    assert task.title is None


def test_task_title_should_be_one_provided_if_passed_in():
    expected = 'Hello werld!'
    task = Task(42, expected)
    assert expected == task.title


def test_proj_id_should_be_none_if_not_passed_in():
    task = Task(42)
    assert task.proj_id is None


def test_proj_id_should_be_one_provided_if_passed_in():
    expected = 'FML'
    task = Task(42, proj_id=expected)
    assert expected == task.proj_id


def test_type_should_be_None_if_not_passed_in():
    assert Task(42).type is None


def test_type_should_be_one_provided_if_passed_in():
    expected = 'Cool Task Type'
    task = Task(42, type=expected)
    assert task.type == expected


def test_reporter_should_be_None_if_not_passed_in():
    assert Task(42).reporter == None


def test_reporter_should_be_one_provided_if_passed_in():
    expected = "April O'Neal"
    task = Task(42, reporter=expected)
    assert task.reporter == expected


def test_owner_should_be_None_if_not_passed_in():
    assert Task(42).owner == None


def test_owner_should_be_one_provided_if_passed_in():
    expected = "More like why don't YOU own the task?"
    task = Task(42, owner=expected)
    assert task.owner == expected


#Project tests
def test_project_should_have_None_values_for_id_title_and_desc_if_not_set():
    p = Project()
    assert p.id is None
    assert p.title is None
    assert p.desc is None


def test_providing_id_to_Project_should_set_it():
    expected = 42
    project = Project(id=expected)
    assert expected == project.id


def test_providing_title_to_Project_should_set_it():
    expected = "Hello Werld"
    project = Project(title=expected)
    assert expected == project.title


def test_providing_Project_desc_should_set_it():
    expected = "Coolest timesheet evar!"
    project = Project(desc=expected)
    assert expected == project.desc


#Timesheet tests
def test_passing_proj_id_to_new_project_should_set_it(timesheet):
    timesheet.new_project(proj_id='Fnord')
    assert 'Fnord' == timesheet.get_project(proj_id='Fnord').id


def test_passing_title_to_new_project_should_set_it(timesheet):
    proj_id = "fnord"
    timesheet.new_project(proj_id=proj_id, title='Do the fnord')
    assert 'Do the fnord' == timesheet.get_project(proj_id).title
    

def test_passing_desc_to_new_project_should_set_it(timesheet):
    proj_id = "fnord"
    timesheet.new_project(proj_id=proj_id, desc='Do the fnord')
    assert 'Do the fnord' == timesheet.get_project(proj_id).desc


def test_passing_project_to_add_project_should_add_it(timesheet):
    proj = Project()
    timesheet.add_project(proj)
    assert proj is timesheet.get_project(proj.id)


def test_should_be_able_to_set_multiple_projects(timesheet):
    proj_one = Project(id=4)
    proj_two = Project(id=2)
    timesheet.add_project(proj_one)
    timesheet.add_project(proj_two)
    assert proj_one is timesheet.get_project(proj_one.id)
    assert proj_two is timesheet.get_project(proj_two.id)


def test_add_project_should_throw_ValueError_if_proj_exists_with_id(timesheet):
    proj_one = Project(id=4)
    timesheet.add_project(proj_one)
    with pytest.raises(ValueError):
        timesheet.add_project(proj_one)


def test_get_project_should_return_None_if_no_proj_exists_with_id(timesheet):
    assert timesheet.get_project('LMF') is None


def test_new_task_should_return_id_for_task(timesheet):
    assert timesheet.new_task() is not None


def test_get_task_should_return_task_if_id_exists(timesheet):
    assert timesheet.get_task(timesheet.new_task()) is not None


def test_new_task_should_set_task_id(timesheet):
    task_id = timesheet.new_task()
    task = timesheet.get_task(task_id)
    assert task.id == task_id


def test_two_calls_to_new_task_should_not_return_same_id(timesheet):
    assert timesheet.new_task() != timesheet.new_task()


def test_new_task_with_title_should_set_it(timesheet):
    expected = 'Heylurrr!'
    task_id = timesheet.new_task(title=expected)
    assert timesheet.get_task(task_id).title == expected


def test_new_task_with_proj_id_should_set_it(timesheet):
    expected = 'No project here!'
    task_id = timesheet.new_task(proj_id=expected)
    assert timesheet.get_task(task_id).proj_id == expected


def test_new_task_with_type_should_set_it(timesheet):
    expected = 'Type? What type?'
    task_id = timesheet.new_task(type=expected)
    assert timesheet.get_task(task_id).type == expected


def test_new_task_with_reporter_should_set_it(timesheet):
    expected = 'Walter Cronkite'
    task_id = timesheet.new_task(reporter=expected)
    assert timesheet.get_task(task_id).reporter == expected


def test_new_task_with_owner_should_set_it(timesheet):
    expected = 'Mister Bigg'
    task_id = timesheet.new_task(owner=expected)
    assert timesheet.get_task(task_id).owner == expected


def test_start_work_on_bad_task_id_should_ValueError(timesheet):
    with pytest.raises(ValueError):
        timesheet.start_work("Does not exist")


def test_start_work_on_good_task_id_should_set_current_task(timesheet):
    task_id = timesheet.new_task()
    timesheet.start_work(task_id)
    assert timesheet.current_task == timesheet.get_task(task_id)


def test_stop_work_should_reset_current_task_to_None(timesheet):
    task_id = timesheet.new_task()
    timesheet.start_work(task_id)
    assume(timesheet.current_task is not None, 'Current task is none')

    timesheet.stop_work()
     
    assert timesheet.current_task is None


def test_add_work_on_bad_task_id_should_ValueError(timesheet):
    with pytest.raises(ValueError):
        timesheet.add_work("Not a real task id", datetime.datetime.now())


def test_add_work_should_add_interval_to_timesheet_intervals(timesheet):
    task_id = timesheet.new_task()
    start = datetime.datetime(1999, 12, 31, 12, 59)
    end = datetime.datetime.now()
    timesheet.add_work(task_id, start, end)
    assert timesheet.intervals[0].task_id == task_id
    assert timesheet.intervals[0].start == start
    assert timesheet.intervals[0].end == end


def test_stop_work_should_set_end_time_on_current_task_to_now(timesheet):
    task_id = timesheet.new_task()
    timesheet.start_work(task_id)
    interval = timesheet.intervals[-1]
    time.sleep(0.1)
    timesheet.stop_work()
    diff = datetime.datetime.now() - interval.end

    assert abs(diff.microseconds) < 100 # Within .0001 seconds


def test_start_work_should_add_new_interval_with_start_of_now(timesheet):
    task_id = timesheet.new_task()
    timesheet.start_work(task_id)
    interval = timesheet.intervals[-1]
    diff = datetime.datetime.now() - interval.start

    assert abs(diff.microseconds) < 100 # Within .0001 seconds
