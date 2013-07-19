#!/usr/bin/env python
'''
Docky Time

Usage:
    dockytime.py 
    dockytime.py --help
    dockytime.py --new-project [--id=ID --title=TITLE --desc=DESC]
    dockytime.py --new-task [--title=TITLE --project=PROJECT --type=TYPE \\
                             --reported-by=REPORTER --assigned-to=OWNER]
    dockytime.py --list-projects [--id=ID]
    dockytime.py --list-tasks [ PROJECT ]
    dockytime.py --start-work ID
    dockytime.py --current-task

Options:
    -h --help            Display this message
    --list-projects      Show list of projects
    --list-tasks         Show list of tasks
    --start-work         Start work on the task with the given ID
    --current-task       List the current task along with time spent info
    PROJECT              ID of the project to filter by
    TITLE                Title of the task/project
    DESC                 Project description
    TYPE                 Type of task, e.g. bug, item, feature
    REPORTER             Person who reported/created the task
    OWNER                Person who should accomplish the task
'''

import yaml
import logging
from docopt import docopt
from clint.textui import colored, indent, puts
from timesheet import *
log = logging.getLogger(__name__)
log.addHandler(logging.FileHandler('time.log'))
log.setLevel(logging.DEBUG)

t = Timesheet()

def save_timesheet():
    data = {'projects':[],
            'tasks':[],
            'intervals':[],
            'notes':[]
            }
    for project in t.projects.values():
        data['projects'].append({'id': project.id,
                                 'title': project.title,
                                 'desc': project.desc})
    for task in t.tasks:
        data['tasks'].append({'id': task.id,
                              'title': task.title,
                              'proj_id': task.proj_id,
                              'type': task.type,
                              'reported_by': task.reporter,
                              'assigned_to': task.owner})

    for interval in t.intervals:
        data['intervals'].append({'task_id':interval.task_id,
                                  'start':interval.start,
                                  'end':interval.end})
    
    text = yaml.dump(data, indent=4)
    log.debug(text)
    with open('data.json', 'w') as f:
        print(text, file=f)


def load_timesheet():
    with open('data.json') as f:
        data = yaml.load(f)

    log.debug('Loaded %s projects', len(data['projects']))
    log.debug('Loaded %s tasks', len(data['tasks']))
    log.debug('Loaded %s intervals', len(data['intervals']))
    log.debug('Loaded %s notes', len(data['notes']))
    for proj in data['projects']:
        p = Project(proj['id'], proj['title'], proj['desc'])
        log.debug("  %s" % p)
        t.add_project(p)

    for task in data['tasks']:
        task = Task(task['id'], task['title'], task['proj_id'], task['type'],
                    task['reported_by'], task['assigned_to'])
        log.debug("  %s" % task)
        t.tasks.append(task)


    for interval in data['intervals']:
        interval = Interval(interval['task_id'],
                            interval['start'],
                            interval['end'])
        log.debug("  %s" % interval)
        t.intervals.append(interval)


def create_project(id, title, desc):
    p = Project()
    p.title = id or input("Project title: ")
    p.id = title or input("Project id: ")
    p.desc = desc or input("Project description: ")

    print(p)
    choice = input("Add Project? [(o)k/(c)ancel/(r)eset]: ").lower()
    if choice == 'o':
        t.add_project(p)
    elif choice == 'c':
        return
    elif choice == 'r':
        new_project()

    save_timesheet()


def list_projects():
    load_timesheet()
    for proj in sorted(t.projects.values()):
        puts(str(proj))


def list_tasks(proj_id):
    load_timesheet()
    for task in t.tasks:
        if proj_id is None or task.proj_id.lower() == proj_id.lower():
            print(task)


def create_task(title, proj_id, type, reporter, owner):
    load_timesheet()
    print('Adding task...')
    title = title or input("Title: ")
    proj_id = proj_id or input('Project ID: ')
    type = type or input("Task type: ")
    reporter = reporter or input("Reported by: ")
    owner = owner or input("Assigned to: ")
    t.new_task(title, proj_id, type, reporter, owner)
    save_timesheet()


def start_work(id):
    load_timesheet()
    t.start_work(id)
    print('Work started on task:\n  ', colored.cyan(t.current_task.title))
    save_timesheet()


def show_current_task():
    load_timesheet()
    if t.current_task is None:
        print("Not working on anything right now...")
        return
    hours = 0.0
    for interval in t.intervals:
        if interval.task_id == t.current_task.id:
            hours += interval.time_spent
    print('Hours spent: ', colored.cyan("{:.2f}".format(hours)))
    print(t.current_task)


if __name__ == "__main__":
    arguments = docopt(__doc__, version='Docky Time v.0.0.1')
    if arguments.get('--list-projects'):
        list_projects()
    elif arguments.get('--new-project'):
        create_project(arguments.get('ID'), 
                       arguments.get('TITLE'),
                       arguments.get('DESC'))
    elif arguments.get('--list-tasks'):
        list_tasks(arguments.get('PROJECT'))
    elif arguments.get('--new-task'):
        create_task(arguments.get('TITLE'),
                    arguments.get('PROJECT'),
                    arguments.get('TYPE'),
                    arguments.get('REPORTER'),
                    arguments.get('OWNER'))
    elif arguments.get('--start-work'):
        start_work(int(arguments.get('ID')))
    elif arguments.get('--current-task'):
        show_current_task()
    else:
        print(arguments)
