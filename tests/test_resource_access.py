from base64 import b64encode
import unittest

from app.models.user import User
from tests import BaseTestClass


class TestRegisterAccess(BaseTestClass, unittest.TestCase):

    def test_post_request_creates_new_user(self):
        response = self.test_client.post('/api/register', json={"username": "test", "password": "pass"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(response.json, "User(username='test')")

    def test_post_request_with_duplicate_username_fails(self):
        json = {"username": "test", "password": "pass"}
        self.test_client.post('/api/register', json=json)
        response = self.test_client.post('/api/register', json=json)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(User.query.count(), 1)


class TestGetTokenAccess(BaseTestClass, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.test_client.post('/api/register', json={"username": "test", "password": "pass"})

    def test_post_request_with_invalid_username_fails(self):
        response = self.test_client.get('/api/token',
                headers={'Authorization': b'Basic ' + b64encode(b'test:invalid')})
        self.assertEqual(response.status_code, 401)

    def test_post_request_with_invalid_password_fails(self):
        response = self.test_client.get('/api/token',
                headers={'Authorization': b'Basic ' + b64encode(b'invalid:pass')})
        self.assertEqual(response.status_code, 401)

    def test_post_request_with_valid_username_and_password_returns_token(self):
        response = self.test_client.get('/api/token',
                headers={'Authorization': b'Basic ' + b64encode(b'test:pass')})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('token' in response.json)


class TestAddExerciseAccess(BaseTestClass, unittest.TestCase):

    def test_post_request_with_invalid_token_fails(self):
        response = self.test_client.post('/api/exercise',
                headers={'Authorization': 'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)


class TestAddRecordAccess(BaseTestClass, unittest.TestCase):

    def test_post_request_with_invalid_token_fails(self):
        response = self.test_client.post('/api/sessions',
                headers={'Authorization': 'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)


class TestGetExercisesAccess(BaseTestClass, unittest.TestCase):

    def test_get_request_with_invalid_token_fails(self):
        response = self.test_client.get('/api/exercises',
                headers={'Authorization': 'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)


class TestGetSessionsAccess(BaseTestClass, unittest.TestCase):

    def test_get_request_with_invalid_token_fails(self):
        response = self.test_client.get('/api/sessions',
                headers={'Authorization': 'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)


class TestDeleteSessionAccess(BaseTestClass, unittest.TestCase):

    def test_post_request_with_invalid_token_fails(self):
        response = self.test_client.delete('/api/sessions/2019-01-01',
                headers={'Authorization': 'Bearer invalid_token'})
        self.assertEqual(response.status_code, 401)
