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
    timesheet.add_interval(project="timesheet",
                           task="Make up some stuff",
                           date="2013-01-29",
                           start="10:01 PM",
                           end="10:05 PM")

    timesheet.add_interval(project="Sleep"
                           task="Close my eyes",
                           date="2013-01-29",
                           start="10:15 PM"
                           end="5:30 AM")

    timesheet.add_interval(project="Kids",
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

