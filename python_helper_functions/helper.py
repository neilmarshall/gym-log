import datetime
import random

from sqlalchemy.exc import IntegrityError

from app import create_app, db
from app.models.exercise import Exercise
from app.models.gym_record import GymRecord
from app.models.session import Session
from app.models.user import User
from config import Config

class BaseHelper():

    def __init__(self):
        Config.SQLALCHEMY_ECHO = True
        self.app = create_app(Config)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def add_to_database(self):
        try:
            db.session.add(self.object)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


class ExerciseHelper(BaseHelper):

    def __init__(self, exercise_name):
        super().__init__()
        self.object = Exercise(exercise_name=exercise_name)

    @classmethod
    def create_exercises(cls):
        exercises = ['bulgarian split squat',
                     'cable flys',
                     'dumbbell bench press',
                     'dumbbell step up',
                     'seated barbell press',
                     'seated dumbbell curl',
                     'seated row',
                     'tricep pushdown',
                     'underhand lat pulldown']
        for exercise in exercises:
            yield cls(exercise)

    @classmethod
    def get_random_exercise(cls):
        exercises = Exercise.query.all()
        return random.choice(exercises)

class UserHelper(BaseHelper):

    def __init__(self, username, password):
        super().__init__()
        self.object = User(username=username)
        self.object.set_password(password)

    @classmethod
    def create_users(cls):
        users = [('Desiree Wartonby', 'dipodomysdeserti'),
                 ('Jorry Collibear', 'cebusapella'),
                 ('Candie Boatwright', 'pitangussulphuratus'),
                 ('Sheena Janaud', 'upupaepops'),
                 ('Beulah Addionizio', 'limnocoraxflavirostra'),
                 ('Max Breen', 'loxodontaafricana'),
                 ('Hadlee Poure', 'macropusrufogriseus'),
                 ('Carline MacVanamy', 'iguanaiguana')]
        for username, password in users:
            yield cls(username, password)

    @classmethod
    def get_random_user(cls):
        users = User.query.all()
        return random.choice(users)


class SessionHelper(BaseHelper):

    def __init__(self, date, user_id):
        super().__init__()
        self.object = Session(date=date, user_id=user_id)

    @classmethod
    def create_random_session(cls):
        date = datetime.date.fromordinal(random.randint(737060, 737424))
        user =  UserHelper.get_random_user()
        return SessionHelper(date=date, user_id=user.id)

    @classmethod
    def get_random_session(cls):
        sessions = Session.query.all()
        return random.choice(sessions)


class GymRecordHelper(BaseHelper):

    def __init__(self, session_id, exercise_id, reps, weight):
        super().__init__()
        self.object = GymRecord(session_id=session_id, exercise_id=exercise_id, reps=reps, weight=weight)

    @classmethod
    def create_random_gym_record(cls, session_id=None):
        if not session_id:
            session_id = SessionHelper.get_random_session().session_id
        exercise_id = ExerciseHelper.get_random_exercise().exercise_id
        reps = random.randint(1, 15)
        weight = random.randint(10, 120)
        return GymRecordHelper(session_id, exercise_id, reps, weight)

    @classmethod
    def get_random_gym_record(cls):
        gym_records = GymRecord.query.all()
        return random.choice(gym_records)
