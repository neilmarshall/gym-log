from datetime import datetime

from app import db

class Session(db.Model):
    """Object relational model of user sessions"""

    __tablename__ = "sessions"

    session_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    records = db.relationship('gym_records', backref='session')

    def __repr__(self):
        return f"Session(date='{self.date}', user_id='{self.user_id}')"
