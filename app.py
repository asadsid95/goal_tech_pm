from flask import Flask, render_template,url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DevelopmentConfig
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@127.0.0.1:3306/test"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#-------------------------------------------

# @app.route("/", methods=["GET", "POST"])
def registration():

    # if request.method=="POST":
    #     print(username)    
    #     username=request.form("username")
    #     formData = User(username )
    #     db.session.add(formData)
    
    return render_template("registration.html", title="Registration")

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
        return f'<User {self.username}>'
