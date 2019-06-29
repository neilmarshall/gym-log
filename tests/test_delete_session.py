from base64 import b64encode
import unittest
import unittest.mock as mock

from sqlalchemy.exc import IntegrityError

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

    def test_delete_session_with_valid_date_in_data_deletes_session(self):
        self.assertEqual(Session.query.count(), 3)
        response = self.test_client.delete('/api/delete-session/2019-06-30',
                headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(Session.query.count(), 2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, "Session for user 'test' on '2019-06-30' deleted")

    def test_delete_session_with_valid_date_not_in_data_leaves_sessions_unchanged(self):
        self.assertEqual(Session.query.count(), 3)
        response = self.test_client.delete('/api/delete-session/2019-06-29',
                headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(Session.query.count(), 3)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Session for user 'test' on '2019-06-29' not found")

    @mock.patch.object(db.session, 'delete')
    def test_delete_session_with_sql_failure_informs_user(self, MockDeleteSession):
        MockDeleteSession.side_effect = IntegrityError('', [], None)
        self.assertEqual(Session.query.count(), 3)
        response = self.test_client.delete('/api/delete-session/2019-06-30',
                headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(Session.query.count(), 3)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Session for user 'test' on '2019-06-30' failed to delete")

    def test_delete_session_with_invalid_date_leaves_sessions_unchanged(self):
        self.assertEqual(Session.query.count(), 3)
        response = self.test_client.delete('/api/delete-session/2019-06-29xxx',
                headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(Session.query.count(), 3)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'],
                "Bad date parameter provided '2019-06-29xxx' - could not be parsed in format 'YYYY-MM-DD'")
