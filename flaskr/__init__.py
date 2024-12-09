from flask import Flask

# functions name needs to be create_app
def create_app():
    
    app = Flask(__name__)
    @app.route("/")
    def hello():
        return "hellow from __init__"
    
    return app