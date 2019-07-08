from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()

from app.resources.exercises import Exercises
from app.resources.register import Register
from app.resources.sessions import Sessions
from app.resources.token import Token

def create_app(config_object=Config):
    """Application Factory"""
    
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)
    api.add_resource(Exercises, '/api/exercises')
    api.add_resource(Register, '/api/register')
    api.add_resource(Sessions, '/api/sessions', '/api/sessions/<session_date>')
    api.add_resource(Token, '/api/token')

    return app
