from flask import Flask
from flask_restful import Resource

app = Flask(__name__)

class Register(Resource):
    def post(self):
        return {'hello': 'world'}


class GetToken(Resource):
    def post(self):
        return {'hello': 'world'}


class AddRecord(Resource):
    def post(self):
        return {'hello': 'world'}


class GetRecord(Resource):
    def get(self):
        return {'hello': 'world'}
