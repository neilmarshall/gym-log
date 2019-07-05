from flask_restful import Resource

from app import db
from app.models.exercise import Exercise
from app.resources import token_auth

class GetExercises(Resource):
    @token_auth.login_required
    def get(self):
        exercises = db.session \
                      .query(Exercise.exercise_name) \
                      .order_by(Exercise.exercise_name) \
                      .all()
        return [e[0] for e in exercises], 200
