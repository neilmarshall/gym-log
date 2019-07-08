from base64 import b64encode
import unittest

from tests import BaseTestClass

from app import db
from app.models.exercise import Exercise

class TestGetExercises(BaseTestClass, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.test_client.post('/api/register', json={'username': 'test', 'password': 'pass'})
        self.token = self.test_client.get('/api/token',
                                          headers={'Authorization': b'Basic ' + b64encode(b'test:pass')}) \
                                     .json.get('token')

        for ex in ['exercise1', 'exercise2', 'exercise3']:
            db.session.add(Exercise(exercise_name=ex))
        db.session.commit()

    def test_get_exercises_returns_correct_exercises(self):
        response = self.test_client.get('/api/exercises', headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, ['exercise1', 'exercise2', 'exercise3'])
