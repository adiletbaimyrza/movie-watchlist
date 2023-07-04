import os
from dotenv import load_dotenv
from flask import Flask
from pymongo import MongoClient

from movie_watchlist.routes import pages


load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["MONGODB_URI"] = os.getenv("MONGODB_URI")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.db = MongoClient(app.config["MONGODB_URI"])["petprojects"]
    app.register_blueprint(pages)
    
    return app