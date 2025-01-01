from flask import Flask, render_template,url_for, request,redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from config import DevelopmentConfig
import pymysql
pymysql.install_as_MySQLdb()
import bcrypt
from datetime import datetime, timedelta

from forms import RegisterForm, LoginForm, EntryForm

#------------------------------------------
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

app.config['SESSION_PERMANENT'] = False


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
            # if (user_in_db.loginAttempt > 5):
            #     flash(f'Account with username "{username}" is locked. Please try again in 1 minute.')
            #     return render_template("login.html", title="Login", form=login_form)

                if not reset_user_loginAttempts(user_in_db):
                    flash(f'Account with username "{username}" is locked. Please try again in 1 minute.')
                    return render_template("login.html", title="Login", form=login_form)
                    
            # else:
                if (bcrypt.checkpw(password.encode('utf-8'), user_in_db.password_hash.encode('utf-8'))):
                
                # reset login_attempts to 0 and failed attempt time to none
                    user_in_db.loginAttempt = 0
                    user_in_db.last_failed_login = None
                    
                    db.session.commit()
                    
                    #TODO: Investigate why cookie is being created outside of this scope such as visiting any other page.
                    session["username"] = user_in_db.username
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
            flash(f'Username "{username}" does not exist', "error")
            return render_template("login.html", title="Login", form=login_form)
                
    else:    
        return render_template("login.html", title="Login", form=login_form)

@app.route("/")
def home():
    
    if "username" in session:
        print(session)
        
        entry_form=EntryForm()
        
        
        return render_template("home.html", title="Home", form=entry_form)
    else:
        print("no session exist")
        return render_template("not_found.html",reason='Session')
    
#-------------------------------------------
#Helper function

def reset_user_loginAttempts(user_in_db):
    if user_in_db.loginAttempt >= 5:
        # when current time has not exceeded 1 minute
        if  datetime.now() < user_in_db.last_failed_login + timedelta(minutes=1):
            print('time has not passed 1 minute')
            return False
        else:
            user_in_db.loginAttempt = 0
            user_in_db.last_failed_login = None
            db.session.commit()
            print("account is now unlocked")
    else:
        return True

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

entry_tags = db.Table(
    'entry_tags',
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Entry(db.Model):
    __tablename__ = "entry"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240), nullable = False)
    content =db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tags = db.relationship('tag', secondary=entry_tags, back_populates='entries')

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    entries = db.relationship('entry', secondary=entry_tags, back_populates='tags')
    
    