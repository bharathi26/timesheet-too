from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SelectField, FloatField, \
                    HiddenField


class TaskForm(Form):
    id = HiddenField()
    project = SelectField('Project:')
    type = SelectField('Type:')
    status = SelectField('Status:')
    title = TextField('Title:')
    contact = TextField('Contact:')
    assigned_to = SelectField('Assigned To:')
    current_estimate = FloatField('Current Estimate:')
    comment = TextAreaField('Comment:')
