from datetime import datetime

from flask import abort, g
from flask_restful import fields, marshal_with, Resource

from app import db
from app.resources.api import token_auth
from app.models.session import ResponseObject, Session

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

