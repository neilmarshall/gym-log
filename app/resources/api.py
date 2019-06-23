from datetime import datetime

from flask import Flask, g, jsonify, make_response, request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_restful import fields, marshal_with, Resource, reqparse
from flask_restful.inputs import date

from app import db
from app.models.exercise import Exercise
from app.models.gym_record import GymRecord
from app.models.session import Session
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
            return make_response(jsonify("ERROR; Please select a unique username"), 409)

        # create new User object
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return make_response(jsonify(repr(user)), 201)


class GetToken(Resource):
    @http_auth.login_required
    def post(self):
        user = User.query.filter(User.username == request.authorization.username).first()
        user.set_token()
        db.session.commit()
        return make_response(jsonify({'token': user.access_token}), 201)


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
        return make_response(jsonify({'Message': 'Exercises successfully created'}), 201)

    def parse_exercises(self, exercises):
        exercises = set(exercises if isinstance(exercises, list) else [exercises])
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
        db.session.add(gym_session)
        db.session.commit()

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

        return make_response(jsonify({'Message': 'Record successfully created'}), 201)

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
    record_fields = {'reps': fields.List(fields.Integer)}

    @token_auth.login_required
    @marshal_with(fields={'session': {'date': fields.DateTime(dt_format='rfc822'),
                                      'username': fields.String(),
                                      'exercises': fields.List(fields.String()),
                                      'reps': fields.List(fields.List(fields.Integer())),
                                      'weights': fields.List(fields.List(fields.Integer()))}})
    def get(self):
        sessions = db.session.query(Session).filter_by(user_id = g.current_user.id).all()
        response_objects = [ResponseObject(session) for session in sessions]
        return response_objects


class ResponseObject():
    def __init__(self, session):
        self.session = session
        self.date = session.date
        self.records = session.records
        self.username = User.query.get(session.user_id).username
        self.records = {}
        for record in session.records:
            exercise_name = db.session \
                              .query(Exercise.exercise_name) \
                              .filter_by(exercise_id = record.exercise_id) \
                              .scalar()
            if exercise_name in self.records:
                self.records[exercise_name]['reps'].append(record.reps)
                self.records[exercise_name]['weights'].append(record.weight)
            else:
                self.records[exercise_name] = {'reps': [record.reps],
                                               'weights': [record.weight]}
        self.exercises = list(self.records.keys())
        self.reps = [self.records[e]['reps'] for e in self.records]
        self.weights = [self.records[e]['weights'] for e in self.records]

    def __repr__(self):
        return f"ResponseObject({self.session})"
