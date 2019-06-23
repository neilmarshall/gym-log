from base64 import b64encode
from datetime import datetime
import unittest

from flask import jsonify

from tests import BaseTestClass

class TestAddRecordJSONValidation(BaseTestClass, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.test_client.post('/api/register', json={'username': 'test', 'password': 'pass'})
        self.token = self.test_client.post('/api/get-token',
                                           headers={'Authorization': b'Basic ' + b64encode(b'test:pass')}) \
                                     .json.get('token')
        self.json = {"date" : "2019-06-30",
                     "exercises" : [{"exercise name" : "exercise1", "reps": [8, 8, 8], "weight": [100, 100, 100]},
                                    {"exercise name" : "exercise2", "reps": [6, 5], "weight": [100, 100]},
                                    {"exercise name" : "exercise3", "reps": [12, 10, 8, 6], "weight": [120, 100, 80, 60]}]}

    def test_add_record_fails_on_missing_date(self):
        self.json.pop('date')
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('date' in response.json['message'])

    def test_add_record_fails_on_bad_date_format(self):
        self.json['date'] = "abc123"
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('date' in response.json['message'])

    def test_add_record_fails_on_missing_exercises(self):
        self.json.pop('exercises')
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('exercises' in response.json['message'])

    def test_add_record_fails_when_exercises_value_is_not_iterable(self):
        self.json['exercises'] = 42
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('exercises' in response.json['message'])

    def test_add_record_fails_when_exercises_value_does_not_contain_exercise_name(self):
        self.json['exercises'][0].pop('exercise name')
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('exercises' in response.json['message'])

    def test_add_record_fails_when_exercises_value_does_not_contain_reps(self):
        self.json['exercises'][0].pop('reps')
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('exercises' in response.json['message'])

    def test_add_record_fails_when_exercises_value_does_not_contain_weight(self):
        self.json['exercises'][0].pop('weight')
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('exercises' in response.json['message'])
