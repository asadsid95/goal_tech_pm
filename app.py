from flask import Flask, render_template,url_for, request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DevelopmentConfig
import pymysql
pymysql.install_as_MySQLdb()

from forms import RegisterForm

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@127.0.0.1:3306/test"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#-------------------------------------------

@app.route("/", methods=["GET", "POST"])
def registration():
    form = RegisterForm()
    print(request.method)
    if request.method == "POST":
        user = User(username=form.username.data, email=form.email.data, password_hash=form.password.data)
        print(user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        print("fail")
        return render_template("registration.html", title="Registration", form=form)
    
    # return render_template("registration.html", title="Registration", form=form)

@app.route("/login")
def login():
    return render_template("login.html")

#-------------------------------------------

# User model
class User(db.Model):                  
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<User {self.username} {self.email} {self.password_hash}>'
