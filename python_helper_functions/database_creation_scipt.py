import random

from python_helper_functions.helper import *

USERS_TO_CREATE = 6
EXERCISES_TO_CREATE = 12
SESSIONS_TO_CREATE = 120
MIN_RECORDS_PER_SESSION = 1
MAX_RECORDS_PER_SESSION = 8

def create_database():
    users = [UserHelper.create_random_user() for _ in range(USERS_TO_CREATE)]
    for user in users:
        user.add_to_database()

    exercises = [ExerciseHelper.create_random_exercise() for _ in range(EXERCISES_TO_CREATE)]
    for exercise in exercises:
        exercise.add_to_database()

    sessions = [SessionHelper.create_random_session() for _ in range(SESSIONS_TO_CREATE)]
    for session in sessions:
        session.add_to_database()

    for session in sorted(sessions, key=lambda s: s.object.date):
        gym_records = [GymRecordHelper.create_random_gym_record(session.object.session_id)
                       for _ in range(random.randint(MIN_RECORDS_PER_SESSION,
                                                     MAX_RECORDS_PER_SESSION))]
        for gym_record in gym_records:
            gym_record.add_to_database()
