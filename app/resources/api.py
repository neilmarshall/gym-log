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


class DeleteSession(Resource):
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
                except IntegrityError:
                    db.session.rollback()
                    abort(400, f"Session for user '{g.current_user.username}' on '{date.date()}' failed to delete")
            else:
                abort(400, f"Session for user '{g.current_user.username}' on '{date.date()}' not found")
        except ValueError:
            abort(400, f"Bad date parameter provided '{session_date}' - could not be parsed in format 'YYYY-MM-DD'")
