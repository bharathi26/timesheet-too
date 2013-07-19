import logging
import datetime
import json
from timesheet import Timesheet, Project, Task, Interval
from clint.textui import puts, colored, indent
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.FileHandler(filename='time.log'))

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
    
    text = json.dumps(data, indent=4)
    log.debug(text)
    with open('data.json', 'w') as f:
        print(text, file=f)


def load_timesheet():
    with open('data.json') as f:
        data = json.load(f)

    log.debug('Loaded %s projects', len(data['projects']))
    log.debug('Loaded %s tasks', len(data['tasks']))
    log.debug('Loaded %s intervals', len(data['intervals']))
    log.debug('Loaded %s notes', len(data['notes']))
    for proj in data['projects']:
        p = Project(proj['id'], proj['title'], proj['desc'])
        log.debug("  %s" % p)
        t.add_project(p)


def new_project():
    p = Project()
    p.title = input("Project title: ")
    p.id = input("Project id: ")
    p.desc = input("Project description: ")

    print(p)
    choice = input("Add Project? [(o)k/(c)ancel/(r)eset]: ").lower()
    if choice == 'o':
        t.add_project(p)
    elif choice == 'c':
        return
    elif choice == 'r':
        new_project()


def list_projects():
    for proj in sorted(t.projects.values()):
        with indent(2):
            puts(colored.cyan(str(proj)))


def main_menu():
    load_timesheet()
    valid_choices = ('1', '2', '3', 'q', 'quit')
    while True:
        print()
        puts(colored.cyan("1.") + " New Project")
        puts(colored.cyan("2.") + " List Projects")
        puts(colored.red("Q. Quit"))
        choice = input("Choice: ")
        print()
        log.debug(choice)

        if choice in ('q', 'quit'):
            return
        elif choice == '1':
            new_project()
        elif choice == '2':
            list_projects()


        if choice not in valid_choices:
            print("Not a valid choice!\n")

        save_timesheet()


if __name__ == "__main__":
    main_menu()
