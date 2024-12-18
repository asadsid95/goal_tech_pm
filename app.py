from flask import Flask, render_template,url_for, request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from config import DevelopmentConfig
import pymysql
pymysql.install_as_MySQLdb()
import bcrypt

from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#-------------------------------------------

@app.route("/", methods=["GET", "POST"])
def registration():
    form = RegisterForm()
    if request.method == "POST":
        
        hashed_password=bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
    
        if db.session.query(User).filter(User.username == form.username.data).first():
            flash( "Username already exist, please choose another username.","error")
            return  render_template("registration.html", title="Registration", form=form)
        else:
            try:
                db.session.add(user)
                db.session.commit()
                flash("User created successfully!", "success")
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                return "Something went wrong. Try again."
    else:
        return render_template("registration.html", title="Registration", form=form)
    


@app.route("/login", methods=["GET","POST"])
def login():
    login_form = LoginForm()
    if request.method =="POST":
        username=login_form.username.data
        password=login_form.password.data
        
        #TODO How to filter by also converting password from form to hash in order to match query results 
        # for user in db.session.query(User).filter(User.username==username, User.password_hash==password).all():
        for user in db.session.query(User).filter(User.username==username).all():
            if (user.username == username and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))):
                return redirect(url_for('home'))
            
        return "Username does not exist"
        # return "Logged in!"
    else:    
       return render_template("login.html", title="Login", form=login_form)

@app.route("/home")
def home():
    return render_template("home.html", title="Home")
#-------------------------------------------

# User model
class User(db.Model):                  
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    isVerified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'User {self.username} {self.email} {self.password_hash}'
