import datetime
import logging 
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey,\
                       Float, DateTime, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask import flash

log = logging.getLogger('boog_slayer.models')

engine = create_engine('sqlite:///timesheet.sq3')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Project(Base):
    __tablename__ = 'projects'

    id = Column(String, primary_key=True)
    name = Column(String)
    charge_code = Column(String)
    desc = Column(String)
    tasks = relationship("Task", backref="project")


    def __init__(self, name, id, charge_code, desc):
        self.name = name
        self.id = id
        self.charge_code = charge_code
        self.desc = desc


    def __repr__(self):
        return "<Project {} - {}>".format(self.id, self.name)


    def __lt__(self, other):
        return self.id < other


    def hours_spent_by_user(self, username):
        return sum(task.hours_spent_by_user(username) for task in self.tasks)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    proj_id = Column(String, ForeignKey('projects.id'))
    type = Column(String)
    assigned_to = Column(String, ForeignKey('users.username'))
    contact = Column(String)
    current_estimate = Column(Float)
    original_estimate = Column(Float)
    comments = relationship("Comment", backref="task")
    intervals = relationship("Interval", backref="task")
    status = Column(String)


    def __init__(self, proj_id, title, type, status, assigned_to, contact):
        self.proj_id = proj_id
        self.title = title
        self.type = type
        self.status = status
        self.assigned_to = assigned_to
        self.contact = contact


    def __repr__(self):
        return "<Task {} - {}>".format(self.proj_id, self.title)


    def hours_spent_by_user(self, username, start=None, end=None):
        log.debug("%s %s", start, end)
        if start is None or end is None:
            return sum(i.hours_spent for i in self.intervals if i.username == username)
        else:
            return sum(i.hours_spent_between(start, end)
                            for i in self.intervals if i.username == username)


    @property
    def time_spent(self):
        return sum(i.hours_spent for i in self.intervals)


class Comment(Base):
    __tablename__ = 'comments'

    task_id = Column(Integer, ForeignKey('tasks.id'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    text = Column(String)
    author = Column(String, ForeignKey('users.username'))


    def __init__(self, task_id, text, timestamp, author):
        self.task_id = task_id
        self.text = text
        self.timestamp = timestamp
        self.author = author


    def __repr__(self):
        return "<Comment: {} - {}>".format(self.timestamp, self.text)


class Edit(Base):
    __tablename__ = 'edits'

    id = Column(Integer, primary_key=True)
    field = Column(String)
    comment_timestamp = Column(DateTime, ForeignKey('comments.timestamp'))
    comment_task_id = Column(Integer, ForeignKey('comments.task_id'))
    old_value = Column(String)
    new_value = Column(String)



class Interval(Base):
    __tablename__ = 'intervals'

    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('users.username'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    start = Column(DateTime)
    end = Column(DateTime, nullable=True)

    def __init__(self, task_id, username, start, end=None):
        self.task_id = task_id
        self.username = username
        self.start = start
        self.end = end


    def __repr__(self):
        return "<Interval task: {} time spent: {:.2f} hrs>".format(self.task,
                                                                   self.hours_spent)


    @property
    def hours_spent(self):
        end = self.end or datetime.datetime.now()
        return (end - self.start).total_seconds()/60/60


    def hours_spent_between(self, start, end):
        now = datetime.datetime.now()
        # Pick the latest start time
        if self.start < start:
            self.start = start
        # Earliest end time
        if self.end is None:
            if now < end:
                self.end = now
            else:
                self.end = end

        if self.end < start:
            self.end = start
                
        end = self.end if end > (self.end or datetime.datetime.now()) else end
        log.debug('Start: %s', start)
        log.debug('End: %s', end)
        log.debug("%s %s", self.start, self.end)
        return self.hours_spent


class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    fullname = Column(String)
    password = Column(String)
    intervals = relationship("Interval", backref="user")
    assigned_tasks = relationship("Task", backref="user")
    comments = relationship("Comment", backref="user")


    def __init__(self, username, fullname, password):
        self.username = username
        self.fullname = fullname
        self.password = password


    def __repr__(self):
        return "<User '{}' '{}'>".format(self.username, self.fullname)


    @property
    def current_task(self):
        for i in self.intervals:
            if i.end is None:
                return i.task
        return None


    @property
    def timesheet(self):
        projects = {}
        tasks = set()
        for i in self.intervals:
            projects[i.task.project] = projects.get(i.task.project, {})
            projects[i.task.project][i.task] = projects[i.task.project].get(
                                                                    i.task, [])
            projects[i.task.project][i.task].append(i)
        
        return projects


    def hours_spent_on_task(self, task_id):
        total = 0
        for i in self.intervals:
            if i.task.id == task_id:
                total += i.hours_spent
        return total


    def is_authenticated(self):
        return True


    def is_active(self):
        return True


    def is_anonymous(self):
        return False


    def get_id(self):
        return self.username

def time_spent_on_project(proj_id, username):
    total = 0
    for i in session.query(Interval).filter_by(username=username):
        if i.task.proj_id == proj_id:
            total += i.hours_spent
    return total


def get_user(username):
    # This will ensure that no errors get the session in a bad state...
    # Each request will either pass thru or if it needs it it will roll
    # the sesssion back.
    session.rollback() 
    return session.query(User).filter_by(username=username).first()


def create_user(username, fullname, password):
    user = User(username, fullname, password)
    session.add(user)
    session.commit()
    return user


def add_project(id, name, charge_code, desc):
    proj = Project(name, id, charge_code, desc)
    session.add(proj)
    session.commit()
    return proj


def list_projects():
    return session.query(Project).all()


def add_task(title, type, status, proj_id, assigned_to, contact, desc, estimate, user):
    task = Task(proj_id, title, type, status, assigned_to, contact)
    if estimate:
        task.original_estimate = estimate
        task.current_estimate = estimate
    session.add(task)
    session.commit()
    if desc:
        comment = Comment(task.id, desc, datetime.datetime.now(), user.username)
        session.add(comment)
    session.commit()
    return task


def update_task(id, proj_id, title, type, status, assigned_to, contact, comment, estimate, user):
    task = get_task(id)
    if task is None:
        return "No task with id {}".format(id)
    if comment:
        comment = Comment(id, comment, datetime.datetime.now(), user.username)
        session.add(comment)
    if estimate:
        task.current_estimate = estimate
        task.original_estimate = task.original_estimate or estimate
    task.proj_id = proj_id
    task.title = title
    task.type = type
    task.status = status
    task.assigned_to = assigned_to
    task.contact = contact
    session.add(task)
    session.commit()
    return 'Updated task: '.format(task)

def get_task(id):
    return session.query(Task).filter_by(id=id).first()


def list_tasks():
    tasks = session.query(Task).all()
    return tasks


def stop_work(id, username):
    interval = session.query(Interval).filter_by(task_id=id,
                                                 username=username,
                                                 end=None).first()
    interval.end = datetime.datetime.now()
    session.add(interval)
    session.commit()
    return interval


def start_work(id, username):
    previous = session.query(Interval).filter_by(username=username,
                                                 end=None).first()
    task = session.query(Task).filter_by(id=id).one()
    task.status = 'In Progress'
    session.add(task)
    interval = Interval(id, username, datetime.datetime.now())
    if previous:
        previous.end = interval.start
        session.add(previous)
    session.add(interval)
    session.commit()
    return interval, previous


def timesheet(date, user):
    morning = datetime.datetime(date.year, date.month, date.day, 0, 0, 0)
    evening = datetime.datetime(date.year, date.month, date.day, 23, 59, 59)
    return session.query(Interval).filter(Interval.username == user.username) \
                                  .filter(Interval.start >= morning) \
                                  .filter(Interval.start <= evening) \
                                  .order_by(Interval.start).all()


def update_times(date, form, username):
    task_ids = form.getlist('task_id')
    ids = form.getlist('id')
    starts = form.getlist('start')
    ends = form.getlist('end')
    changes = set()
    log.debug(task_ids)
    for task_id, id, start, end in zip(task_ids, ids, starts, ends):
        interval = session.query(Interval).get(id)
        if interval is None:
            log.debug('Interval is none')
            interval = Interval(task_id, username, start, end)
            session.add(interval)
            changes.add(interval)
        start = datetime.datetime.strptime(start, "%I:%M %p").replace(
                                                            year=date.year,
                                                            month=date.month,
                                                            day=date.day)

        if end:
            end = datetime.datetime.strptime(end, "%I:%M %p").replace(
                                                            year=date.year,
                                                            month=date.month,
                                                            day=date.day)
        else:
            end = None
        if interval.start != start:
            interval.start = start
            session.add(interval)
            changes.add(interval)
        if interval.end != end:
            interval.end = end
            session.add(interval)
            changes.add(interval)
        session.commit()

    return changes
    

def get_status_report(user, start, end):
    intervals = session.query(Interval) \
                       .filter(Interval.username == user.username) \
                       .filter(Interval.start >= start) \
                       .filter(or_(Interval.end <= end, Interval.end == None)) \
                       .order_by(Interval.start) \
                       .all()
    projects = {}
    tasks = set()
    for i in intervals:
        projects[i.task.project] = projects.get(i.task.project, {})
        projects[i.task.project][i.task] = projects[i.task.project].get(
                                                                i.task, [])
        projects[i.task.project][i.task].append(i)
    
    return projects


def delete_interval(interval_id, user):
    try:
        interval = session.query(Interval).filter_by(username = user.username,
                                                     id = interval_id).one()
        message = "Deleted {}".format(str(interval))
        session.delete(interval)
        session.commit()
        return message
    except NoResultFound:
        return "Could not find interval"
    except MultipleResultsFound:
        return "Found too many intervals?"


def list_users():
    return session.query(User).all()


def list_task_types():
    return (('Bug', 'Bug'),
            ('Task', 'Task'),
            ('Feature', 'Feature'),
           )


def list_status_types():
    return (('New','New'),
            ('In Progress','In Progress'),
            ('Closed - Complete','Closed - Complete'),
            ('Closed - Duplicate','Closed - Duplicate'),
            ("Closed - Won't fix","Closed - Won't fix"),
           )


Base.metadata.create_all(engine)
