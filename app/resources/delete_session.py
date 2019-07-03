from datetime import datetime

from flask import abort, g
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.gym_record import GymRecord
from app.models.session import Session
from app.resources import token_auth

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
