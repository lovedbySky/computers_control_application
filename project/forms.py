from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class Terminal(FlaskForm):
    command = StringField('command', validators=[DataRequired()])
    submit = SubmitField("execute")


class Login(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = StringField("password", validators=[DataRequired()])
    submit = SubmitField("login")
