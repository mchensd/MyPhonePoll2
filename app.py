from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from forms import LoginForm, SurveyForm, DestroySurveyForm
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Shell, Manager

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)


app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABSE_URL') or \
                                        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'

manager = Manager(app)
bootstrap = Bootstrap(app)

db = SQLAlchemy(app)
from models import User, PhoneNumber
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Number=PhoneNumber)


manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))

app.config['SID'] = os.environ.get('account_sid')
app.config['TOK'] = os.environ.get("auth_token")



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect("/")
    return render_template("login.html", form=form)


@app.route("/profile/<id>")
def profile(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template("profile.html", user=user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/receiver/<id>", methods=['GET', 'POST'])
def receiver(id):
    ph = PhoneNumber.query.get(id)
    choices = eval(ph.choices)
    resp = MessagingResponse()
    if not ph.in_use:
        resp.message("This phone number doesn't have a survey associated with it yet")

    else:
        client = Client(app.config['SID'], app.config['TOK'])
        in_msg = client.messages.list()[0]
        if in_msg.from_[1:] == ph.number:
            return


        resp.message("That option is not a choice on the survey")
        if in_msg.body.lower() in choices:
            choices[in_msg.body.lower()] += 1
            resp.message("Your vote has been counted!")

    return str(resp)


@app.route("/phonenumbers/<id>", methods=['GET', 'POST'])
def phone_view(id):
    ph = PhoneNumber.query.get(id)
    print(ph.in_use)
    if ph.in_use:
        form = DestroySurveyForm()
        if form.validate_on_submit():
            ph.destroy_survey()
            return redirect(url_for('phone_view', id=id))
        poll=eval(ph.choices)
        return render_template('poll_view.html', title=ph.title, poll=poll, form=form)
    else:
        form = SurveyForm()
        if form.validate_on_submit():

            print(form.choices.data)
            choices = form.choices.data
            while '' in choices:
                choices.remove('')
                print(choices)

            count = {}
            for choice in choices:
                choice = choice.lower()
                count[choice]=0
                print(count)
            ph.make_survey(count)
            ph.title = form.title.data
            db.session.commit()
            print("Redirecting")
            return redirect(url_for('phone_view', id=id))


        return render_template("new_poll.html", form=form)

if __name__ == '__main__':
    manager.run()

