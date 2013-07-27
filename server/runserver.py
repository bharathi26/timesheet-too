import os
import models
import forms
import datetime
from flask import Flask
from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask.ext.login import LoginManager, current_user, login_user, \
                            logout_user, login_required
import logging
log = logging.getLogger('boog_slayer')

boog_slayer = Blueprint('boog_slayer', __name__, template_folder='templates')


@boog_slayer.route('/')
def main():
    return render_template('index.html')


@boog_slayer.route('/status-report', defaults={"start":None, "end":None})
@boog_slayer.route('/status-report/<start>/<end>')
@login_required
def status_report(start, end):
    return render_template('status_report.html',
                           report=models.get_status_report(current_user,
                                                           start,
                                                           end))


@boog_slayer.route('/projects', methods=['GET', 'POST'])
def projects():
    form = forms.project.ProjectForm()
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
    form = forms.task.TaskForm()
    form.project.choices = tuple((p.id, '{} - {}'.format(p.name, p.id))
                                        for p in models.list_projects())
    form.assigned_to.choices = tuple((u.username, u.fullname) 
                                        for u in models.list_users())
    form.type.choices = models.list_task_types()
    form.status.choices = models.list_status_types()
    if id is None:
        if request.method == 'POST':
            task = models.add_task(request.form.get('title'),
                                   request.form.get('type'),
                                   request.form.get('status'),
                                   request.form.get('proj_id'),
                                   request.form.get('assigned_to'),
                                   request.form.get('contact'),
                                   request.form.get('desc'),
                                   request.form.get('estimate'),
                                   current_user)
            flash('Added task {}'.format(task))
        return render_template('tasks.html',
                               tasks=models.list_tasks(),
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
        task = models.get_task(id)
        form.assigned_to.data = current_user.username
        form.status.default = task.status
        form.type.default = task.type
        form.project.default = task.project.id
        form.process()
        form.id.data = id
        form.title.data = task.title
        form.contact.data = task.contact
        form.current_estimate.data = task.current_estimate
        return render_template('task.html', task=task, form=form)


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
    return redirect(request.args.get('next') or url_for('.tasks', id=id))


@boog_slayer.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.login.LoginForm()
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
    app = Flask('foo')
    app.register_blueprint(boog_slayer)
    app.secret_key = 'This should be something different'.encode()
    login_manager = LoginManager()
    login_manager.init_app(app)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)


    @login_manager.user_loader
    def load_user(userid):
        return models.get_user(userid)
    port = int(os.environ.get('TASK_PORT') or 5000)
    app.run('0.0.0.0', port=port, debug=True)
