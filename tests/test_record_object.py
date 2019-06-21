from base64 import b64encode
import unittest

from tests import BaseTestClass

class TestRecordObject(BaseTestClass, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.test_client.post('/api/register', json={'username': 'test', 'password': 'pass'})
        self.token = self.test_client.post('/api/get-token',
                                           headers={'Authorization': b'Basic ' + b64encode(b'test:pass')}) \
                                     .json.get('token')
        self.json = {"date" : "date",
                     "exercises" : [{"exercise name" : "exercise1", "reps": [8, 8, 8], "weight": [100, 100, 100]},
                                    {"exercise name" : "exercise2", "reps": [6, 5], "weight": [100, 100]},
                                    {"exercise name" : "exercise3", "reps": [12, 10, 8, 6], "weight": [120, 100, 80, 60]}]}

    def test_add_record_validates_date(self):
        self.json['date'] = None
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('expected error message' in response.json)

    def test_add_record_validates_exercises(self):
        self.json['exercises'] = None
        response = self.test_client.post('/api/add-record',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json=self.json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue('expected error message' in response.json)
