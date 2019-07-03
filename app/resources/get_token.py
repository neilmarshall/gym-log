from flask import request
from flask_restful import Resource

from app import db
from app.models.user import User
from app.resources import http_auth

class GetToken(Resource):
    @http_auth.login_required
    def get(self):
        user = User.query.filter(User.username == request.authorization.username).first()
        user.set_token()
        db.session.commit()
        return {'token': user.access_token}
