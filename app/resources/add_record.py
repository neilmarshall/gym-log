from sqlalchemy.exc import IntegrityError

from flask import g
from flask_restful import Resource, reqparse
from flask_restful.inputs import date

from app import db
from app.models.exercise import Exercise
from app.models.gym_record import GymRecord
from app.models.session import Session
from app.resources.api import token_auth

class AddRecord(Resource):
    @token_auth.login_required
    def post(self):
        # validate JSON data
        parser = reqparse.RequestParser()
        parser.add_argument('date', type=date, required=True, case_sensitive=False, location='json')
        parser.add_argument('exercises', type=self.parse_exercises, required=True, case_sensitive=False, location='json')
        data = parser.parse_args(strict=True)

        # create a gym session object
        gym_session = Session(date=data['date'], user_id=g.current_user.id)
        try:
            db.session.add(gym_session)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {'message': 'error: sessions must be unique across dates for each user'}, 400

        # create gym record objects and link the to the session
        for exercise in data['exercises']:
            exercise_id = db.session \
                            .query(Exercise.exercise_id) \
                            .filter_by(exercise_name = exercise['exercise name']) \
                            .scalar()
            for reps, weight in zip(exercise['reps'], exercise['weights']):
                record = GymRecord(session_id=gym_session.session_id,
                                   exercise_id=exercise_id,
                                   reps=reps,
                                   weight=weight)
                db.session.add(record)
                db.session.commit()

        return {'Message': 'Record successfully created'}, 201

    def parse_exercises(self, exercises):
        try:
            for exercise in exercises:
                exercise_name = exercise['exercise name']
                exercise_id = db.session \
                                .query(Exercise.exercise_id) \
                                .filter_by(exercise_name = exercise['exercise name']) \
                                .scalar()
                if exercise_id is None:
                    raise ValueError(f"Exercise '{exercise_name}' not recognised - please add as an exercise")
                reps = list(map(int, exercise['reps']))
                weights = list(map(int, exercise['weights']))
                if len(reps) != len(weights):
                    raise ValueError(f"Mismatch between 'reps' ({reps}) and 'weights' ({weights})")
            return exercises
        except KeyError as e:
            raise ValueError(f'Missing required parameter {e} in the JSON body')
