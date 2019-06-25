from base64 import b64encode
from datetime import datetime
import unittest

from tests import BaseTestClass

from app import db
from app.models.exercise import Exercise
from app.models.session import Session

class TestGetRecord(BaseTestClass, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.test_client.post('/api/register', json={'username': 'test', 'password': 'pass'})
        self.token = self.test_client.get('/api/get-token',
                                          headers={'Authorization': b'Basic ' + b64encode(b'test:pass')}) \
                                     .json.get('token')

        for ex in ['exercise1', 'exercise2', 'exercise3']:
            db.session.add(Exercise(exercise_name=ex))
        db.session.commit()

        json1 = {"date" : "2019-05-31",
                 "exercises" : [{"exercise name" : "exercise1", "reps": [8, 8, 8], "weights": [100, 100, 100]},
                                {"exercise name" : "exercise2", "reps": [6, 5], "weights": [100, 100]},
                                {"exercise name" : "exercise3", "reps": [12, 10, 8, 6], "weights": [120, 100, 80, 60]}]}

        json2 = {"date" : "2019-06-30",
                 "exercises" : [{"exercise name" : "exercise1", "reps": [8, 8, 8], "weights": [100, 100, 100]},
                                {"exercise name" : "exercise3", "reps": [12, 10, 8], "weights": [120, 80, 60]}]}

        json3 = {"date" : "2019-07-31",
                 "exercises" : [{"exercise name" : "exercise1", "reps": [8, 8, 8], "weights": [100, 100, 100]},
                                {"exercise name" : "exercise2", "reps": [8, 7, 6], "weights": [100, 110, 120]}]}

        response = self.test_client.post('/api/add-record', headers={'Authorization': 'Bearer ' + self.token}, json=json1)
        response = self.test_client.post('/api/add-record', headers={'Authorization': 'Bearer ' + self.token}, json=json2)
        response = self.test_client.post('/api/add-record', headers={'Authorization': 'Bearer ' + self.token}, json=json3)

    def test_get_sessions_returns_formatted_data(self):
        response = self.test_client.get('/api/get-sessions', headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(response.status_code, 200)
        sessions = response.json
        session1, session2, session3 = sessions

        self.assertEqual(session1['session'],
                         {'date': 'Fri, 31 May 2019 00:00:00 -0000',
                          'username': 'test',
                          'exercises': ['exercise1', 'exercise2', 'exercise3'],
                          'reps': [[8, 8, 8], [6, 5], [12, 10, 8, 6]],
                          'weights': [[100, 100, 100], [100, 100], [120, 100, 80, 60]]})

        self.assertEqual(session2['session'],
                         {'date': 'Sun, 30 Jun 2019 00:00:00 -0000',
                          'username': 'test',
                          'exercises': ['exercise1', 'exercise3'],
                          'reps': [[8, 8, 8], [12, 10, 8]],
                          'weights': [[100, 100, 100], [120, 80, 60]]})

        self.assertEqual(session3['session'],
                         {'date': 'Wed, 31 Jul 2019 00:00:00 -0000',
                          'username': 'test',
                          'exercises': ['exercise1', 'exercise2'],
                          'reps': [[8, 8, 8], [8, 7, 6]],
                          'weights': [[100, 100, 100], [100, 110, 120]]})

    def test_get_single_session_returns_formatted_data(self):
        response = self.test_client.get('/api/get-sessions/2', headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(response.status_code, 200)
        session = response.json[0]

        self.assertEqual(session['session'],
                         {'date': 'Sun, 30 Jun 2019 00:00:00 -0000',
                          'username': 'test',
                          'exercises': ['exercise1', 'exercise3'],
                          'reps': [[8, 8, 8], [12, 10, 8]],
                          'weights': [[100, 100, 100], [120, 80, 60]]})
