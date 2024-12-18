from flaskr import create_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flaskr import db
import pymysql
pymysql.install_as_MySQLdb

# app=create_app()
# print(app)

# db = SQLAlchemy(app)
# migrate=Migrate(app, db)

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


