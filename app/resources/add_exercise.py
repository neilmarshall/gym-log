from flask_restful import Resource, reqparse

from app import db
from app.models.exercise import Exercise
from app.resources.api import token_auth

class AddExercise(Resource):
    @token_auth.login_required
    def post(self):
        # validate JSON data
        parser = reqparse.RequestParser()
        parser.add_argument('exercises', type=self.parse_exercises, required=True, case_sensitive=False, location='json')
        data = parser.parse_args(strict=True)

        # create new Exercise object
        for exercise_name in data['exercises']:
            db.session.add(Exercise(exercise_name=exercise_name))
        db.session.commit()
        return {'Message': 'Exercises successfully created'}, 201

    def parse_exercises(self, exercises):
        exercises = set(exercises if isinstance(exercises, list) else [exercises])
        exercises = {e.title().strip() for e in exercises}
        for exercise in exercises:
            if db.session \
                 .query(Exercise) \
                 .filter_by(exercise_name = exercise) \
                 .first() is not None:
                raise ValueError(f"Error - '{exercise}' already exists in database")
        return exercises
