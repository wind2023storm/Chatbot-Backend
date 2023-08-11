from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv
from rich import print, pretty
pretty.install()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:wind2023storm@localhost/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .chat import chat as chat_blueprint
    chat_blueprint.db = db
    app.register_blueprint(chat_blueprint)

    from .message import message as message_blueprint
    message_blueprint.db = db
    app.register_blueprint(message_blueprint)

    return app