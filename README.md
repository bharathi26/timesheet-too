timesheet
=========

A simple Python-based timesheet library.

This project is under development and is very *very* beta.


Design
======

This is a **DRAFT** and is totally subject to change. I'm entertaining all
sorts of ideas at the moment, so if you want something changed, now would be a
good time ;)


##Example usage


    from timesheet import Timesheet

    timesheet = Timesheet()
    timesheet.add_time(project="timesheet",
                           task="Make up some stuff",
                           date="2013-01-29",
                           start="10:01 PM",
                           end="10:05 PM")

    timesheet.add_time(project="Sleep"
                           task="Close my eyes",
                           date="2013-01-29",
                           start="10:15 PM"
                           end="5:30 AM")

    timesheet.add_time(project="Kids",
                           task="Comfort screaming child",
                           date="2013-01-30",
                           start="12:30 AM",
                           end="1:45 AM")

    for day in timesheet:
        print("Date:", day.date)

        for span in day:
            print("    Project:", span.project)
            print("    Task:", span.task)
            print("    Start:", span.start)
            print("    End:", span.end)
            print("    Elapsed:", span.elapsed)

    print("Sleep: ", timesheet.project('Sleep').time_spent)
    # Example output:

    2013-01-29:
        Project: timesheet
        Task: Make up some stuff
        Start: 10:01 PM
        End: 10:05 PM
        Elapsed: 0h 4m

        Project: Sleep
        Task: Close my eyes
        Start: 10:15 PM
        End: 12:00 AM
        Elapsed: 1h 45m

    2013-01-30:
        Project: Sleep
        Task: Close my eyes
        Start: 12:00 AM
        End: 12:30 AM
        Elapsed: 0h 30m

        Project: Kids
        Task: Comfort screaming child
        Start: 12:30 AM
        End: 1:45 AM
        Elapsed: 1h 15m

        Project: Sleep
        Task: Close my eyes
        Start: 1:45 AM
        End: 5:30 AM
        Elapsed: 3h 45m

    Sleep: 6h 45m


**Another example:**
    
    timesheet = Timesheet()
    # Add a bunch of time

    start = datetime(2010, 8, 14)
    end = datetime(2010, 8, 15)
    for project in timesheet.time_spent(start=start, end=end, type='projects'):
        print("Project: {0}\nTime Spent: {1}".format(project.name,
                                                     project.time_spent))


    # Output:
    Project: Sleep
    Time Spent: 3h 42m

    Project: Cool Thing
    Time Spent: 42h

Adding time will automagically do the right(?) thing. You don't have to wory
about you or your users making mistakes.  Let's say you've setup your 
timesheet and add the following:

    timesheet.add_time("7:00 AM", "5:00 PM", task="Do the thing")

but you realized that this was the wrong task. So if you go ahead and do:

    timesheet.add_time("7:00 AM", "5:00 PM", task="Do ALL the things!")

Then the previous time interval will be overwritten. If for some reason you
might want to back this up, you can, because `add_time()` will always return
the original state of all intervals that it modifies. So in this case, you'd
get an Interval back for 7:00 AM - 5:00 PM today, with a task of "Do the
thing".

This will work the same for all kinds of modifications or overlap, so all
that would be required to undo the operation would be something like:

    old_stuff = timesheet.add_time("12:00 AM",
                                   "11:59 PM",
                                   task="You're insane!",
                                   project="No Face")

    for interval in old_stuff:
        timesheet.add_time(interval.start,
                           interval.end,
                           interval.task,
                           interval.project,
                           interval.date)

You may also clear time off your timesheet with the `clear_time()` function,
which just takes a start and end time, and a date. It will return the same
thing as `add_time` - the previous value of any interval that it modifies.
