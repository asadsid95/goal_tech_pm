from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired,Length

class RegisterForm(FlaskForm):
    username = StringField("Username",[DataRequired(),Length(min=4, message=("username is too short"))])
    email= StringField("Email", [DataRequired(),Length(min=4, message=("email is too short"))])
    password=StringField("Password", [DataRequired(),Length(min=4, message=("password is too short"))])
    submit=SubmitField("Register")

