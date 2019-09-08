from flask import abort, make_response, jsonify
from flask_restful import Resource, reqparse

from app import db
from app.models.exercise import Exercise
from app.resources import token_auth

class Exercises(Resource):

    @token_auth.login_required
    def get(self):
        exercises = db.session \
                      .query(Exercise.exercise_name) \
                      .order_by(Exercise.exercise_name) \
                      .all()
        return [e[0] for e in exercises], 200

    @token_auth.login_required
    def post(self):
        # validate JSON data
        parser = reqparse.RequestParser()
        parser.add_argument('exercises', type=self.parse_exercises, required=True, case_sensitive=False, location='json')
        exercises = parser.parse_args(strict=True)['exercises']

        # return 409 if content duplicated
        for exercise in exercises:
            if db.session \
                 .query(Exercise) \
                 .filter_by(exercise_name = exercise) \
                 .first() is not None:
                abort(409)

        # create new Exercise object
        for exercise_name in exercises:
            db.session.add(Exercise(exercise_name=exercise_name))
        db.session.commit()

        return exercises, 201

    def parse_exercises(self, exercises):
        exercises = exercises if isinstance(exercises, list) else [exercises]
        exercises = [' '.join(e.title().strip().split()) for e in exercises]
        return tuple(sorted(set(exercises)))
