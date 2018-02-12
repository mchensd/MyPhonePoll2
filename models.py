from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True)
    age = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))

    phone_numbers = db.relationship("PhoneNumber", backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError("Password is not a readable property")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return '<User {} {}>'.format(self.first_name, self.last_name)

class PhoneNumber(db.Model):
    __tablename__ = 'phone_numbers'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    in_use = db.Column(db.Boolean, default=False)
    choices = db.Column(db.String(512))
    title = db.Column(db.String(64))

    def make_survey(self, choices):
        self.choices = repr(choices)
        self.in_use = True
        db.session.commit()

    def destroy_survey(self):
        self.choices = '{}'
        self.in_use = False
        db.session.commit()

    def __repr__(self):
        return '<{}>'.format(self.number)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)