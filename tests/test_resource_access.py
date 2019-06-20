import unittest

from app.models.user import User
from tests import BaseTestClass


class TestRegisterAccess(BaseTestClass, unittest.TestCase):

    def test_post_request_creates_new_user(self):
        json = {"username": "test", "password": "pass"}
        response = self.test_client.post('/api/register', json=json)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.query.count(), 1)

    def test_post_request_with_duplicate_username_fails(self):
        json = {"username": "test", "password": "pass"}
        self.test_client.post('/api/register', json=json)
        response = self.test_client.post('/api/register', json=json)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(User.query.count(), 1)


class TestGetTokenAccess(BaseTestClass, unittest.TestCase):

    def test_post_request_with_invalid_username_fails(self):
        self.fail()

    def test_post_request_with_invalid_password_fails(self):
        self.fail()

    def test_post_request_with_valid_username_and_password_returns_token(self):
        self.fail()


class TestAddRecordAccess(BaseTestClass, unittest.TestCase):

    def test_post_request_with_invalid_token_fails(self):
        self.fail()

    def test_post_request_with_valid_token_succeeds(self):
        self.fail()


class TestGetRecordAccess(BaseTestClass, unittest.TestCase):

    def test_get_request_with_invalid_token_fails(self):
        self.fail()

    def test_get_request_with_valid_token_succeeds(self):
        self.fail()
