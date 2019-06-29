from datetime import datetime

from sqlalchemy.exc import IntegrityError

from flask import abort, Flask, g, request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_restful import fields, marshal_with, Resource, reqparse
from flask_restful.inputs import date

from app import db
from app.models.exercise import Exercise
from app.models.gym_record import GymRecord
from app.models.session import ResponseObject, Session
from app.models.user import User

http_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@http_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    return user is not None and user.check_password(password)


@token_auth.verify_token
def verify_token(access_token):
    user = User.query.filter_by(access_token=access_token).first()
    if user is None or user.token_expiry < datetime.utcnow():
        return False
    g.current_user = user  # set current user on global object
    return True


class Register(Resource):
    def post(self):
        # validate JSON data
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, case_sensitive=False)
        parser.add_argument('password', required=True, case_sensitive=False)
        data = parser.parse_args(strict=True)
        username, password = data['username'], data['password']

        # ensure username is unique
        if User.query.filter_by(username=username).first() is not None:
            return "ERROR; Please select a unique username", 409

        # create new User object
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return repr(user), 201


class GetToken(Resource):
    @http_auth.login_required
    def get(self):
        user = User.query.filter(User.username == request.authorization.username).first()
        user.set_token()
        db.session.commit()
        return {'token': user.access_token}


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


class GetSessions(Resource):
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
            except ValueError:
                abort(400, f"Bad date parameter provided '{session_date}' - could not be parsed in format 'YYYY-MM-DD'")
        return [ResponseObject(session) for session in sessions]
