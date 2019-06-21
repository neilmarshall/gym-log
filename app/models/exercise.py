from app import db

class Exercise(db.Model):
    """Object relational model of exercises"""

    __tablename__ = "exercises"

    exercise_id = db.Column(db.Integer, primary_key=True)
    exercise_name = db.Column(db.String(128), unique=True, nullable=False)

    records = db.relationship('gym_records', backref='exercise')

    def __repr__(self):
        return f"Exercise(exercise_name='{self.exercise_name}')"
