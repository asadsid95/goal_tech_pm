from flask import Flask, render_template,url_for, request,redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from config import DevelopmentConfig

import pymysql
pymysql.install_as_MySQLdb()

import bcrypt
from datetime import datetime, timedelta
from flask_wtf import CSRFProtect
from forms import RegisterForm, LoginForm, EntryForm

import os
from dotenv import find_dotenv, load_dotenv
from authlib.integrations.flask_client import OAuth

#------------------------------------------
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# for k,v in app.config.items():
#     print(f'k:{k}, v:{v}')

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
    
app.secret_key = os.environ.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.environ.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

app.config['SESSION_PERMANENT'] = False
# csrf = CSRFProtect(app)

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
    
@app.route("/login1", methods=["GET","POST"])
def login1():
    login_form = LoginForm()

    print(login_form.validate_on_submit())
    if login_form.validate_on_submit():
  
        print("valdiated")
        username=login_form.username.data
        password=login_form.password.data
        
        user_in_db = db.session.query(User).filter(User.username == username).first()
        if user_in_db:

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
                    session['user_id'] = user_in_db.id
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
        print("validate didn't pass")
        print("Error:", login_form.errors)
    return render_template("login.html", title="Login", form=login_form)

@app.route('/login')
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )
    
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    print(session['user'])
    return redirect("/")



@app.route("/", methods=["GET", "POST"])
def home():
    
    # if "username" in session and request.method == "POST":
    entry_form=EntryForm()
    if "username" in session:

        # show all existing entries
        if request.method =="GET":
            
            
            return render_template("home.html", title="Home", form=entry_form)
        
        elif request.method=="POST":
            
            title = entry_form.title.data
            content=entry_form.content.data
            tag=entry_form.tag.data
            
            # To add entry, I need to get user.id and tag.id before sending query to add the entry
            
            check_tag = db.session.query(Tag).filter(Tag.name==tag).first()
            if not check_tag:
                return f"Tag {tag} does not exist."
            tag_id = check_tag.id
            
            user_id = session["user_id"]
            user_entry=Entry(title=title, content=content, user_id=user_id, tag_id=tag_id)
                       
            db.session.add(user_entry)
            db.session.commit()
        
        return render_template("home.html", title="Home", form=entry_form)
    else:
        print("no session exist")
        return render_template("not_found.html",reason='Session')

@app.route("/temp_entries", methods=["GET"])
def TEMP_show_entries():
    
    existing_entries = db.session.query(Entry).all()
    
    return render_template("temp_show_entries.html", entries = existing_entries)
    
# Endpoint to add tags 
@app.route("/tag_create", methods=["POST"])
def tag_create():

    #TODO - Add tags into database table 'Tag'
    tags_from_client = request.get_json().get("tag")
    # print(tags_from_client.values())
    
    for tag in tags_from_client:
        tag_to_add = Tag(name=tag)
        db.session.add(tag_to_add)
        db.session.commit()
    
    
    return "tag added"

@app.route('/test')
def test():
    
   return render_template('navigation.html')
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
    
    # entries = db.relationship('Entry', backref='user', lazy=True)

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
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=True)

    # user = db.relationship('User', backref="entries")
    
    # tags = db.relationship('Tag', secondary=entry_tags, back_populates='entries')
    
    def __repr__(self) -> str:
        return f"Entry {self.title} {self.content} user_id:{self.user_id} tag_id{self.tag_id}"

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # entries = db.relationship('Entry', secondary=entry_tags, back_populates='tags')
    
    def __repr__(self) -> str:
        return f"Tag {self.name}"
