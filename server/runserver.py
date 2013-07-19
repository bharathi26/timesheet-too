import models
from flask import Flask, render_template
from flask.ext.login import LoginManager, current_user

app = Flask(__name__)
app.secret_key = 'This should be something different'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    return models.GetUser(userid)


@app.route('/')
def main():
    return render_template('base.html')


@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == "__main__":
    app.run('0.0.0.0', port=8765, debug=True)
