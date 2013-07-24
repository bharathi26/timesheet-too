import models
import forms
import datetime
from flask import Flask, render_template, url_for, redirect, flash, request
from flask.ext.login import LoginManager, current_user, login_user, \
                            login_required

app = Flask(__name__)
app.secret_key = 'This should be something different'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    return models.get_user(userid)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/status-report', defaults={"start":None, "end":None})
@app.route('/status-report/<start>/<end>')
@login_required
def status_report(start, end):
    return render_template('status_report.html',
                           report=models.get_status_report(current_user,
                                                           start,
                                                           end))


@app.route('/projects', methods=['GET', 'POST'])
def projects():
    if request.method == 'POST':
        proj = models.add_project(request.form.get('id'),
                                  request.form.get('name'),
                                  request.form.get('charge_code'),
                                  request.form.get('desc'))
        flash("Added project: {}".format(proj))
    return render_template('project.html', projects=models.list_projects())


@app.route('/tasks', methods=['GET', 'POST'], defaults={'id':None})
@app.route('/tasks/<id>', methods=['GET', 'POST'])
def tasks(id):
    if id is None:
        if request.method == 'POST':
            task = models.add_task(request.form.get('title'),
                                   request.form.get('type'),
                                   request.form.get('proj_id'),
                                   request.form.get('assigned_to'),
                                   request.form.get('contact'),
                                   request.form.get('desc'),
                                   request.form.get('estimate'),
                                   current_user)
            flash('Added task {}'.format(task))
        return render_template('tasks.html', tasks=models.list_tasks())
    else:
        if request.method == "POST":
            flash(models.update_task(request.form.get('task_id'),
                                     request.form.get('proj_id'),
                                     request.form.get('title'),
                                     request.form.get('type'),
                                     request.form.get('assigned_to'),
                                     request.form.get('contact'),
                                     request.form.get('comment'),
                                     request.form.get('estimate'),
                                     current_user))
        return render_template('task.html', task=models.get_task(id))


@app.route('/start_work/<id>')
@login_required
def start_work(id):
    task, previous_task = models.start_work(id, current_user.username)
    if previous_task:
        flash("Stopped work on {}".format(previous_task))
    flash("Started work on {}".format(task))
    return redirect(request.args.get('next') or url_for('tasks', id=id))


@app.route('/stop_work/<id>')
@login_required
def stop_work(id):
    task = models.stop_work(id, current_user.username)
    flash("Stopped work on {}".format(task))
    return redirect(request.args.get('next') or url_for('tasks', id=id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        flash("Already logged in")
        return redirect(url_for('main'))
    if request.method == 'POST':
        user = models.get_user(request.form.get('username'))
        if (user is None or user.password != request.form.get('password')):
            flash("Error with username/password")
        else:
            login_user(user)
            return redirect(request.args.get('next') or url_for('main'))
    return render_template('login.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated():
        flash("Already registered")
        return redirect(url_for('main'))
    if request.method == 'POST':
        if models.get_user(request.form.get('username')) is None:
            user = models.create_user(request.form.get('username'),
                                      request.form.get('fullname'),
                                      request.form.get('password'))
            login_user(user)
            return redirect(url_for('main'))
        else:
            flash("Error - username is already taken!")
    return render_template('register.html')


@app.route("/timesheet/", methods=['GET', 'POST'], defaults={"date":None}) 
@app.route("/timesheet/<date>", methods=['GET', 'POST'])
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


if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)
