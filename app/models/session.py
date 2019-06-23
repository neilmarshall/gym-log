from datetime import datetime

from app import db
from app.models.exercise import Exercise
from app.models.user import User

class Session(db.Model):
    """Object relational model of user sessions"""

    __tablename__ = "sessions"

    session_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    records = db.relationship('GymRecord', backref='session')

    def __repr__(self):
        return f"Session(date='{self.date}', user_id='{self.user_id}')"


class ResponseObject():
    def __init__(self, session):
        self.date = session.date
        self.username = User.query.get(session.user_id).username
        self.records = {}
        for record in session.records:
            exercise_name = db.session \
                              .query(Exercise.exercise_name) \
                              .filter_by(exercise_id = record.exercise_id) \
                              .scalar()
            if exercise_name in self.records:
                self.records[exercise_name]['reps'].append(record.reps)
                self.records[exercise_name]['weights'].append(record.weight)
            else:
                self.records[exercise_name] = {'reps': [record.reps], 'weights': [record.weight]}
        self.exercises = list(self.records.keys())
        self.reps = [self.records[e]['reps'] for e in self.records]
        self.weights = [self.records[e]['weights'] for e in self.records]
