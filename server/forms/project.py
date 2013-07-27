from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField

class ProjectForm(Form):
    id = TextField('ID:')
    name = TextField('Name:')
    charge_code = TextField('Charge Code:')
    description = TextAreaField('Description:')
