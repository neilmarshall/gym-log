from base64 import b64encode
from datetime import datetime
import unittest

from tests import BaseTestClass

from app import db
from app.models.exercise import Exercise
from app.models.session import Session

class TestAddRecordJSONValidation(BaseTestClass, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.test_client.post('/api/register', json={'username': 'test', 'password': 'pass'})
        self.token = self.test_client.post('/api/get-token',
                                           headers={'Authorization': b'Basic ' + b64encode(b'test:pass')}) \
                                     .json.get('token')
        self.json = {"date" : "2019-06-30",
                     "exercises" : [{"exercise name" : "exercise1", "reps": [8, 8, 8], "weights": [100, 100, 100]},
                                    {"exercise name" : "exercise2", "reps": [6, 5], "weights": [100, 100]},
                                    {"exercise name" : "exercise3", "reps": [12, 10, 8, 6], "weights": [120, 100, 80, 60]}]}

    def test_add_record_fails_on_missing_date(self):
        self.json.pop('date')
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['date'],
                         "Missing required parameter in the JSON body")

    def test_add_record_fails_on_bad_date_format(self):
        self.json['date'] = "abc123"
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['date'],
                         "time data 'abc123' does not match format '%Y-%m-%d'")

    def test_add_record_fails_on_missing_exercises(self):
        self.json.pop('exercises')
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['exercises'],
                         "Missing required parameter in the JSON body")

    def test_add_record_fails_when_exercises_value_is_not_iterable(self):
        self.json['exercises'] = 42
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['exercises'],
                         "'int' object is not iterable")

    def test_add_record_fails_when_exercises_value_does_not_contain_exercise_name(self):
        self.json['exercises'][0].pop('exercise name')
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['exercises'],
                         "Missing required parameter 'exercise name' in the JSON body")

    def test_add_record_fails_when_exercises_value_does_not_contain_reps(self):
        self.json['exercises'][0].pop('reps')
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['exercises'],
                         "Missing required parameter 'reps' in the JSON body")

    def test_add_record_fails_when_exercises_value_does_not_contain_weight(self):
        self.json['exercises'][0].pop('weights')
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['exercises'],
                         "Missing required parameter 'weights' in the JSON body")

    def test_add_record_fails_when_exercises_value_has_length_mismatch_between_reps_and_weights(self):
        self.json['exercises'][0]['reps'].append(99)
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['exercises'],
                         "Mismatch between 'reps' ([8, 8, 8, 99]) and 'weights' ([100, 100, 100])")

    def test_add_record_fails_when_exercises_value_has_non_integer_reps(self):
        self.json['exercises'][0]['reps'][0] = 'abc123'
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['exercises'],
                         "invalid literal for int() with base 10: 'abc123'")


    def test_add_record_fails_when_exercises_value_has_non_integer_weights(self):
        self.json['exercises'][0]['weights'][0] = 'abc123'
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['exercises'],
                         "invalid literal for int() with base 10: 'abc123'")


class TestAddRecordCreatesRecord(BaseTestClass, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.test_client.post('/api/register', json={'username': 'test', 'password': 'pass'})
        self.token = self.test_client.post('/api/get-token',
                                           headers={'Authorization': b'Basic ' + b64encode(b'test:pass')}) \
                                     .json.get('token')
        for ex in ['exercise1', 'exercise2', 'exercise3']:
            db.session.add(Exercise(exercise_name=ex))
        db.session.commit()
        self.json = {"date" : "2019-06-30",
                     "exercises" : [{"exercise name" : "exercise1", "reps": [8, 8, 8], "weights": [100, 100, 100]},
                                    {"exercise name" : "exercise2", "reps": [6, 5], "weights": [100, 100]},
                                    {"exercise name" : "exercise3", "reps": [12, 10, 8, 6], "weights": [120, 100, 80, 60]}]}

    def test_add_record_with_valid_data_creates_a_session(self):
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['Message'], 'Record successfully created')
        session = db.session.query(Session).first()
        self.assertEqual(session.date, datetime.strptime(self.json['date'], "%Y-%m-%d"))
        self.assertEqual(len(session.records), 9)

    def test_add_record_with_valid_data_back_populates_exercises(self):
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['Message'], 'Record successfully created')
        exercises = db.session.query(Exercise).all()
        self.assertEqual(len(exercises[0].records), 3)
        self.assertEqual(len(exercises[1].records), 2)
        self.assertEqual(len(exercises[2].records), 4)

    def test_add_record_with_valid_data_creates_a_record(self):
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['Message'], 'Record successfully created')
        records = db.session.query(Session).first().records

        self.assertEqual(records[0].session_id, 1)
        self.assertEqual(records[0].exercise_id, 1)
        self.assertEqual(records[0].reps, 8)
        self.assertEqual(records[0].weight, 100)

        self.assertEqual(records[-1].session_id, 1)
        self.assertEqual(records[-1].exercise_id, 3)
        self.assertEqual(records[-1].reps, 6)
        self.assertEqual(records[-1].weight, 60)
