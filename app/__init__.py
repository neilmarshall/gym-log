from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()

from app.resources.add_exercise import AddExercise
from app.resources.add_record import AddRecord
from app.resources.delete_session import DeleteSession
from app.resources.get_exercises import GetExercises
from app.resources.get_sessions import GetSessions
from app.resources.get_token import GetToken
from app.resources.register import Register

def create_app(config_object=Config):
    """Application Factory"""
    
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)
    api.add_resource(AddExercise, '/api/add-exercise')
    api.add_resource(AddRecord, '/api/add-record')
    api.add_resource(DeleteSession, '/api/delete-session/<session_date>')
    api.add_resource(GetExercises, '/api/get-exercises')
    api.add_resource(GetSessions, '/api/get-sessions', '/api/get-sessions/<session_date>')
    api.add_resource(GetToken, '/api/get-token')
    api.add_resource(Register, '/api/register')

    return app
