"""
Entry point for 'flask run' command
"""
from app import create_app, db
from app.models.exercise import Exercise
from app.models.gym_record import GymRecord
from app.models.session import Session
from app.models.user import User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Launch a Python interpreter pre-populated with an application context"""
    return {'db': db, 'Exercise': Exercise, 'GymRecord': GymRecord, 'Session': Session, 'User': User}
