from flask_restful import Resource, reqparse

from app import db
from app.models.user import User

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
