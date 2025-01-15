from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
    SESSION_SECRET = os.environ.get("SECRET_KEY")
    SECRET_KEY = os.environ.get("APP_SECRET_KEY")

    DEBUG = True