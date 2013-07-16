timesheet
=========

A simple Python-based timesheet library.

This project is under development and is very *very* beta.

This project uses semantic versioning (see http://semver.org)
v.0.0.1

Design
======


##Example usage

    timesheet = Timesheet()
    timesheet.add_timecodes({42: 'Answer questions',
                             13: 'Bug fixes',
                             99: 'Do something',
                             26: 'Programming})
    timesheet.add_timecode(99, 'Something else')
    timesheet.add_project(id="DTT-3",
                          title="Do the Thing",
                          desc="There is a thing. Do it.",
                          default_time_code=26)
    timesheet.set_defaults(proj_id="DTT-3", time_code=26)
    task_id = timesheet.add_task("Start a thing")
    other_task_id = timesheet.add_task("Start another thing", 
                                       time_code=13,
                                       proj="DTT-3")
    timesheet.start_work(task_id)
    timesheet.start_work("Start another thing") # Stops working on first task
    timesheet.start_work(other_task_id) #no-op, already working on that
    timesheet.start_work("not a real task title")
    ValueError: Cannot start work - no task with title "not a real task title"

    timesheet.add_comment(task_id, "Did some work on this earlier")
    timesheet.stop_work()
    altered_times = timesheet.add_work(task_id,
                                       datetime(2010, 8, 14),
                                       datetime(2010, 8, 14, 10, 0, 0),
                                       'Did loads of work on this. Ten hrs!')
    print(altered_times) #Add work automatically fixes conflicts


    for project in timesheet.projects:
        print(project.id, project.hours_worked)
            for task in project.tasks:
                print(task.title, task.hours_worked)
                    for comment in task.comments:
                        print(comment.tstamp, comment.text)


    for day in timesheet:
        for hour in day:
            for interval in hour:
                print(interval, interval.project, interval.task, interval.note)


##Errors:

    timesheet = Timesheet()
    timesheet.add_task("Fnord")
    ValueError: No default project, and none provided.

    timesheet.add_task("Fnord", proj="Fnordy")
    ValueError: No project with id "Fnordy" exists.

    timesheet.set_defaults(proj_id="Fnords")
    ValueError: No project with id "Fnords" exists

    timesheet.set_defaults(time_code=26)
    ValueError: No time code <26> exists
