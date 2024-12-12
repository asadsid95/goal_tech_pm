from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired,Length

class RegisterForm(FlaskForm):
    username = StringField("Username",[DataRequired(),Length(min=4, message=("username is too short"))])
    submit=SubmitField("Register")
    