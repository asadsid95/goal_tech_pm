from flask import Flask
from config import DevelopmentConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from data import users

# TODO: why do SQLalchemy and Migrate need to be initialized
# This ensure that they are tied to the Flask application instance when it is created.
db = SQLAlchemy()
migrate = Migrate()

# functions name needs to be create_app
def create_app():
    
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    # T
    db.init_app(app)
    migrate.init_app(app, db)
    
    @app.route("/")
    def hello():
        return "hellow from __init__"
    
    return app

