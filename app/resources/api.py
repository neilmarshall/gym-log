from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, reqparse

from app import db
from app.models.user import User

class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, case_sensitive=False)
        parser.add_argument('password', required=True, case_sensitive=False)
        data = parser.parse_args(strict=True)
        username, password = data['username'], data['password']
        if User.query.filter_by(username=username).first() is not None:
            return make_response(jsonify("ERROR; Please select a unique username"), 409)
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return make_response(jsonify(repr(user)), 201)


class GetToken(Resource):
    def post(self):
        return {'hello': 'world'}


class AddRecord(Resource):
    def post(self):
        return {'hello': 'world'}


class GetRecord(Resource):
    def get(self):
        return {'hello': 'world'}
