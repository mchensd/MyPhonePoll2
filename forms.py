from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FieldList, FormField

from wtforms.validators import  DataRequired
class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField("Remember Me?")
    submit = SubmitField("Submit")

class PollChoiceForm(Form):
    choice = StringField()

class SurveyForm(Form):
    title = StringField("Title", validators=[DataRequired()])
    choices = FieldList(StringField("Choice"), min_entries = 10)
    submit = SubmitField("Create Poll!")

class DestroySurveyForm(Form):
    submit = SubmitField("Destroy Survey")