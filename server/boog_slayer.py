import os
import sys
import datetime
from . import models
from .forms import task as task_form
from .forms import project as project_form
from .forms import login as login_form
from flask import Flask
from flask import Blueprint, render_template, url_for, redirect, flash, \
                  request, current_app, session

from flask.ext.login import LoginManager, current_user, login_user, \
                            logout_user, login_required
import logging
log = logging.getLogger('boog_slayer')

boog_slayer = Blueprint('boog_slayer', __name__, template_folder='templates')
boog_slayer.name = __name__


@boog_slayer.route('/')
def main():
    return render_template('index.html')


@boog_slayer.route('/status-report', defaults={"start":None, "end":None})
@boog_slayer.route('/status-report/<start>/<end>')
@login_required
def status_report(start, end):
    offset = 3 - datetime.date.today().weekday()
    if end is None:
        end = datetime.datetime.today() + datetime.timedelta(offset)
    else:
        end = datetime.datetime.strptime(str(end)[:10],
                                         "%Y-%m-%d").replace(hour=23,
                                                             minute=59)
    if start is None:
        start = end - datetime.timedelta(6)
    else:
        start = datetime.datetime.strptime(str(start)[:10], "%Y-%m-%d")
    
    log.debug("{} {}".format(start.date(), end.date()))
    return render_template('status_report.html',
                           report=models.get_status_report(current_user,
                                                           start,
                                                           end),
                           today=datetime.datetime.now(),
                           start=start,
                           span=datetime.timedelta(1),
                           end=end)


@boog_slayer.route('/projects', methods=['GET', 'POST'])
def projects():
    form = project_form.ProjectForm()
    if form.validate_on_submit():
        proj = models.add_project(form.id.data,
                                  form.name.data,
                                  form.charge_code.data,
                                  form.description.data,
                                 )
        flash("Added project: {}".format(proj))
        form.id.data = None
        form.name.data = None
        form.charge_code.data = None
        form.description.data = None
    return render_template('project.html',
                           projects=models.list_projects(),
                           form=form)


@boog_slayer.route('/tasks', methods=['GET', 'POST'], defaults={'id':None})
@boog_slayer.route('/tasks/<id>', methods=['GET', 'POST'])
def tasks(id):
    form = task_form.TaskForm()
    form.project.choices = tuple((p.id, '{} - {}'.format(p.name, p.id))
                                        for p in models.list_projects())
    form.assigned_to.choices = tuple((u.username, u.fullname) 
                                        for u in models.list_users())
    form.type.choices = current_app.config.get('TASK_TYPES') or models.list_task_types()
    form.status.choices = current_app.config.get('STATUSES') or models.list_status_types()
    session['filter'] = request.args.get('filter', session.get('filter'))
    filters = session.get('recent_filters', [])
    try:
        filters.insert(0, filters.pop(filters.index(session['filter'])))
    except ValueError:
        filters.insert(0, session['filter'])
    session['recent_filters'] = filters[:5]
    if id is None:
        if request.method == 'POST':
            task = models.add_task(form.title.data,
                                   form.type.data,
                                   form.status.data,
                                   form.project.data,
                                   form.assigned_to.data,
                                   form.contact.data,
                                   form.comment.data,
                                   form.current_estimate.data,
                                   current_user)
            flash('Added task {}'.format(task))
            
            return redirect(request.args.get('next') 
                         or url_for('.task')+'?id='+str(task.id))
        return render_template('tasks.html',
                               tasks=models.list_tasks(session['filter']),
                               recent_filters=session['recent_filters'],
                               current_filter=session['filter'],
                               form=form,
                               )
    else:
        if request.method == "POST":
            flash(models.update_task(form.id.data,
                                     form.project.data,
                                     form.title.data,
                                     form.type.data,
                                     form.status.data,
                                     form.assigned_to.data,
                                     form.contact.data,
                                     form.comment.data,
                                     form.current_estimate.data,
                                     current_user))
        return redirect(request.args.get('next') or url_for('.task')+'?id='+id)


@boog_slayer.route('/task', methods=['GET', 'POST'])
def task():
    form = task_form.TaskForm()
    form.project.choices = tuple((p.id, '{} - {}'.format(p.name, p.id))
                                        for p in models.list_projects())
    form.assigned_to.choices = tuple((u.username, u.fullname) 
                                        for u in models.list_users())
    form.type.choices = current_app.config.get('TASK_TYPES') or models.list_task_types()
    form.status.choices = current_app.config.get('STATUSES') or models.list_status_types()
    task = models.get_task(request.args.get('id'))
    if task is not None:
        if request.args.get('action') is None:
            form.status.default = task.status
        else:
            form.status.default = models.get_status(request.args.get('action'))
        form.type.default = task.type
        form.project.default = task.project.id
        form.process()
        form.assigned_to.data = task.assigned_to or current_user.get_id()
        form.id.data = task.id
        form.title.data = task.title
        form.contact.data = task.contact
        form.current_estimate.data = task.current_estimate
    else:
        form.assigned_to.data = current_user.get_id()

    return render_template('task.html',
                           task=task,
                           form=form,
                           mode=request.args.get('mode') or 'view')


@boog_slayer.route('/start_work/<id>')
@login_required
def start_work(id):
    task, previous_task = models.start_work(id, current_user.username)
    if previous_task:
        flash("Stopped work on {}".format(previous_task))
    flash("Started work on {}".format(task))
    return redirect(request.args.get('next') or url_for('.tasks', id=id))


@boog_slayer.route('/stop_work/<id>')
@login_required
def stop_work(id):
    task = models.stop_work(id, current_user.username)
    flash("Stopped work on {}".format(task))
    return redirect(request.args.get('next') or url_for('.tasks', id=None))


@boog_slayer.route('/login', methods=['GET', 'POST'])
def login():
    form = login_form.LoginForm()
    if current_user.is_authenticated():
        flash("Already logged in")
        return redirect(url_for('.main'))
    if request.method == 'POST':
        user = models.get_user(request.form.get('username'))
        if (user is None or user.password != request.form.get('password')):
            flash("Error with username/password")
        else:
            login_user(user)
            return redirect(request.args.get('next') or url_for('.main'))
    return render_template('login.html', form=form)


@boog_slayer.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.main'))


@boog_slayer.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated():
        flash("Already registered")
        return redirect(url_for('.main'))
    if request.method == 'POST':
        if models.get_user(request.form.get('username')) is None:
            user = models.create_user(request.form.get('username'),
                                      request.form.get('fullname'),
                                      request.form.get('password'))
            login_user(user)
            return redirect(url_for('.main'))
        else:
            flash("Error - username is already taken!")
    return render_template('register.html')


@boog_slayer.route("/timesheet/", methods=['GET', 'POST'], defaults={"date":None}) 
@boog_slayer.route("/timesheet/<date>", methods=['GET', 'POST'])
@login_required
def timesheet(date):
    if date is None:
        date = datetime.datetime.now().date()
    else:
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    if request.method == 'POST':
        flash(models.update_times(date, request.form, current_user.username))
    return render_template("timesheet.html", 
                           today=date,
                           tomorrow=date+datetime.timedelta(1),
                           yesterday=date-datetime.timedelta(1),
                           intervals=models.timesheet(date, current_user))


@boog_slayer.route("/delete_interval/<id>")
@login_required
def delete_interval(id):
    flash(models.delete_interval(id, current_user))
    return redirect(request.args.get('next') or url_for('.timesheet'))


if __name__ == "__main__":
    class ReverseProxied(object):
        '''Wrap the application in this middleware and configure the 
        front-end server to add these headers, to let you quietly bind 
        this to a URL other than / and to an HTTP scheme that is 
        different than what is used locally.

        In nginx:
        location /myprefix {
            proxy_pass http://192.168.0.1:5001;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Scheme $scheme;
            proxy_set_header X-Script-Name /myprefix;
            }

        :param app: the WSGI application
        '''
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
            if script_name:
                environ['SCRIPT_NAME'] = script_name
                path_info = environ['PATH_INFO']
                if path_info.startswith(script_name):
                    environ['PATH_INFO'] = path_info[len(script_name):]

            scheme = environ.get('HTTP_X_SCHEME', '')
            if scheme:
                environ['wsgi.url_scheme'] = scheme
            return self.app(environ, start_response)

    app = Flask('foo')
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    app.register_blueprint(boog_slayer)
    app.secret_key = 'This should be something different'.encode()
    login_manager = LoginManager()
    login_manager.init_app(app)
    handler = logging.StreamHandler(stream=sys.stdout)
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)


    @login_manager.user_loader
    def load_user(userid):
        return models.get_user(userid)
    port = int(os.environ.get('TASK_PORT') or 5000)
    app.run('0.0.0.0', port=port, debug=True)
