from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

from app.resources.api import *

def create_app(config_object):
    """Application Factory"""
    
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)
    api.add_resource(AddExercise, '/api/add-exercise')
    api.add_resource(AddRecord, '/api/add-record')
    api.add_resource(GetSessions, '/api/get-sessions', '/api/get-sessions/<int:session_id>')
    api.add_resource(GetToken, '/api/get-token')
    api.add_resource(Register, '/api/register')

    return app
