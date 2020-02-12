from datetime import datetime

from sqlalchemy.exc import IntegrityError

from flask import abort, current_app, g
from flask_restful import fields, marshal_with, Resource, reqparse
from flask_restful.inputs import date

from app import db
from app.models.exercise import Exercise
from app.models.gym_record import GymRecord
from app.models.session import ResponseObject, Session
from app.resources import token_auth

class Sessions(Resource):

    @token_auth.login_required
    @marshal_with(fields={'session': {'date': fields.DateTime(dt_format='rfc822'),
                                      'username': fields.String(),
                                      'exercises': fields.List(fields.String()),
                                      'reps': fields.List(fields.List(fields.Integer())),
                                      'weights': fields.List(fields.List(fields.Integer()))}})
    def get(self, session_date=None):
        if session_date is None:
            sessions = db.session \
                         .query(Session) \
                         .filter_by(user_id = g.current_user.id) \
                         .order_by(Session.date) \
                         .all()
        else:
            try:
                date = datetime.strptime(session_date, '%Y-%m-%d')
                sessions = db.session \
                             .query(Session) \
                             .filter_by(date = date) \
                             .filter_by(user_id = g.current_user.id) \
                             .all()
            except ValueError as exn:
                current_app.logger.error(exn.args)
                abort(400, f"Bad date parameter provided '{session_date}' - could not be parsed in format 'YYYY-MM-DD'")
        return [ResponseObject(session) for session in sessions]

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
        except IntegrityError as exn:
            current_app.logger.error(exn.args)
            db.session.rollback()
            return {'message': 'error: sessions must be unique across dates for each user'}, 409

        # create gym record objects and link the to the session
        try:
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
        except Exception as exn:
            current_app.logger.error(exn.args)
            abort(500)

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
        except KeyError as exn:
            current_app.logger.error(exn.args)
            raise ValueError(f'Missing required parameter {exn} in the JSON body')

    @token_auth.login_required
    def delete(self, session_date):
        try:
            date = datetime.strptime(session_date, '%Y-%m-%d')
            session = db.session \
                        .query(Session) \
                        .filter_by(date = date) \
                        .filter_by(user_id = g.current_user.id) \
                        .one_or_none()
            if session:
                try:
                    records = GymRecord.query \
                                       .filter_by(session_id = session.session_id) \
                                       .all()
                    for record in records:
                        db.session.delete(record)
                    db.session.commit()
                    db.session.delete(session)
                    db.session.commit()
                    return f"Session for user '{g.current_user.username}' on '{date.date()}' deleted", 201
                except IntegrityError as exn:
                    current_app.logger.error(exn.args)
                    db.session.rollback()
                    abort(400, f"Session for user '{g.current_user.username}' on '{date.date()}' failed to delete")
            else:
                abort(400, f"Session for user '{g.current_user.username}' on '{date.date()}' not found")
        except ValueError as exn:
            current_app.logger.error(exn.args)
            abort(400, f"Bad date parameter provided '{session_date}' - could not be parsed in format 'YYYY-MM-DD'")
