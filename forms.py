from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired,Length

class RegisterForm(FlaskForm):
    username = StringField("Username",[DataRequired(),Length(min=4, message=("Username is too short"))])
    email= StringField("Email", [DataRequired(),Length(min=4, message=("Email is too short"))])
    password=StringField("Password", [DataRequired(),Length(min=4, message=("Password is too short"))])
    submit=SubmitField("Register")

class LoginForm(FlaskForm):
    username=StringField("Username", [DataRequired(), Length(min=4, message=("Username is too short"))])
    password=StringField("Password", [DataRequired(), Length(min=4, message=("Password is too short"))])
    submit=SubmitField("Login")