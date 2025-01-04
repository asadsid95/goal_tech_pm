from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,SelectField
from wtforms.validators import DataRequired,Length,Email,EqualTo

class RegisterForm(FlaskForm):
    username = StringField("Username",[DataRequired(),Length(min=4, message=("Username is too short. It must be greater than 4 characters."))])
    email= StringField("Email", [DataRequired(),Email()])
    password=StringField("Password", [DataRequired(),Length(min=4, message=("Password is too short"))])
    confirm_password=StringField("Confirm Password", [DataRequired(), EqualTo('password', message="Passwords must match")])
    submit=SubmitField("Register")

class LoginForm(FlaskForm):
    username=StringField("Username", [DataRequired(), Length(min=4, message=("Username is too short"))])
    password=StringField("Password", [DataRequired(), Length(min=4, message=("Password is too short"))])
    submit=SubmitField("Login")
    
class EntryForm(FlaskForm):
    title=StringField("Title of entry", [DataRequired(message="Title is required"), Length(min=4, max=240, message=("Title is too short or long"))])
    content=StringField("Content of entry",  [DataRequired(message="Content is required"), Length(min=4, max=240, message=("Content is too short or long"))])
    tag=SelectField("Tag", choices=[("thought","Thought"),("hobby", 'Hobby'),('career thought', "CareerThought"), ("plant watering", "PlantWatering")])
    submit=SubmitField("Submit entry")