from flask import Flask, render_template,url_for, request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from config import DevelopmentConfig
import pymysql
pymysql.install_as_MySQLdb()
import bcrypt
from datetime import datetime

from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#-------------------------------------------

@app.route("/registration", methods=["GET", "POST"])
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
                #TODO: Verify if method=post in html and redirecting from backend is correct for form submission
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
        
        user_in_db = db.session.query(User).filter(User.username == username).first()
    
        if user_in_db:
            if (bcrypt.checkpw(password.encode('utf-8'), user_in_db.password_hash.encode('utf-8'))):
                
                # reset login_attempts to 0 and failed attempt time to none
                user_in_db.loginAttempt = 0
                user_in_db.last_failed_login = None
                
                db.session.commit()
                
                flash("Successful login", "success")
                return redirect(url_for('home'))
            else:
                
                # increment login_attempts by 1
                user_in_db.loginAttempt += 1
                user_in_db.last_failed_login = datetime.now()
                
                db.session.commit()
                flash("Password does not match", 'error')
                return render_template("login.html", title="Login", form=login_form)
        else:
            flash("Username does not exist", "error")
            return render_template("login.html", title="Login", form=login_form)
                
    else:    
        return render_template("login.html", title="Login", form=login_form)

@app.route("/")
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
    loginAttempt = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'User {self.username} {self.email} {self.password_hash}'
