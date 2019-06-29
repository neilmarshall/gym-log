from datetime import datetime
from itertools import groupby

from sqlalchemy import UniqueConstraint

from app import db
from app.models.exercise import Exercise
from app.models.gym_record import GymRecord
from app.models.user import User

class Session(db.Model):
    """Object relational model of user sessions"""

    __tablename__ = "sessions"

    session_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'date'),)

    records = db.relationship('GymRecord', backref='session')

    def __repr__(self):
        return f"Session(date='{self.date}', user_id='{self.user_id}')"


class ResponseObject():
    def __init__(self, session):
        self.date = session.date
        self.username = User.query.get(session.user_id).username
        data = db.session \
                 .query(Exercise.exercise_name, GymRecord.reps, GymRecord.weight) \
                 .select_from(Exercise) \
                 .join(GymRecord) \
                 .join(Session) \
                 .filter(Session.session_id == session.session_id) \
                 .order_by(Exercise.exercise_name, GymRecord.record_id) \
                 .all()
        self.exercises = [k for k, _ in groupby(data, key=lambda x: x[0])]
        self.reps = [[r[1] for r in v] for _, v in groupby(data, key=lambda x: x[0])]
        self.weights = [[r[2] for r in v] for _, v in groupby(data, key=lambda x: x[0])]
