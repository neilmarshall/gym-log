from base64 import b64encode
import unittest

from tests import BaseTestClass

from app import db
from app.models.exercise import Exercise

class TestAddExerciseJSONValidation(BaseTestClass, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.test_client.post('/api/register', json={'username': 'test', 'password': 'pass'})
        self.token = self.test_client.post('/api/get-token',
                                           headers={'Authorization': b'Basic ' + b64encode(b'test:pass')}) \
                                     .json.get('token')

    def test_add_exercise_fails_on_missing_data(self):
        response = self.test_client.post('/api/add-exercise',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['exercises'],
                         "Missing required parameter in the JSON body")

    def test_add_exercise_fails_if_exercise_already_in_data(self):
        self.test_client.post('/api/add-exercise',
                              headers={'Authorization': 'Bearer ' + self.token},
                              json={"exercises" : "exercise1"})
        response = self.test_client.post('/api/add-exercise',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json={"exercises" : "exercise1"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message']['exercises'],
                         "Error - 'exercise1' already exists in database")

    def test_add_exercise_does_not_add_duplicate_data_multiple_times(self):
        response = self.test_client.post('/api/add-exercise',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json={"exercises" : ["exercise1", "exercise1"]})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(db.session.query(Exercise).count(), 1)


class TestAddExerciseCreatesExercise(BaseTestClass, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.test_client.post('/api/register', json={'username': 'test', 'password': 'pass'})
        self.token = self.test_client.post('/api/get-token',
                                           headers={'Authorization': b'Basic ' + b64encode(b'test:pass')}) \
                                     .json.get('token')

    def test_add_exercise_with_single_exercise_creates_exercise_in_database(self):
        response = self.test_client.post('/api/add-exercise',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json={'exercises': 'exercise1'})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['Message'], 'Exercises successfully created')

        self.assertEqual(db.session.query(Exercise).count(), 1)

        exercise = db.session.query(Exercise).first()
        self.assertEqual(exercise.exercise_name, "exercise1")

    def test_add_exercise_with_multiple_exercises_creates_exercises_in_database(self):
        response = self.test_client.post('/api/add-exercise',
                                         headers={'Authorization': 'Bearer ' + self.token},
                                         json={'exercises': ['exercise1', 'exercise2']})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['Message'], 'Exercises successfully created')

        self.assertEqual(db.session.query(Exercise).count(), 2)

        exercises = db.session.query(Exercise).order_by(Exercise.exercise_name).all()
        self.assertEqual(exercises[0].exercise_name, "exercise1")
        self.assertEqual(exercises[1].exercise_name, "exercise2")
