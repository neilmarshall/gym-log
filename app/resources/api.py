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
