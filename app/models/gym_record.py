from app import db

class GymRecord(db.Model):
    """Object relational model of gym records"""

    __tablename__ = "gym_records"

    record_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.session_id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.exercise_id'), nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Exercise(exercise_name='{self.exercise_name}')"
