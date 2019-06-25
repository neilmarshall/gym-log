import os

from dotenv import load_dotenv
import sqlalchemy

if __name__ == '__main__':
    basedir = os.path.abspath(os.path.split(os.path.dirname(__file__))[0])
    load_dotenv(os.path.join(basedir, '.env'))
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
    conn = engine.connect()

    conn.execute('''
        CREATE OR REPLACE VIEW aggregated_data AS
        SELECT users.username, sessions.date, exercises.exercise_name, gym_records.reps, gym_records.weight
          FROM users
          JOIN sessions ON users.id = sessions.user_id
          JOIN gym_records ON sessions.session_id = gym_records.session_id
          JOIN exercises ON gym_records.exercise_id = exercises.exercise_id
         ORDER BY sessions.date, exercises.exercise_name;''')

    conn.execute('''
        CREATE OR REPLACE VIEW sessions_with_duplicate_id_date_combinations AS
        SELECT session_id
          FROM sessions
         WHERE user_id IN (SELECT user_id
                             FROM sessions
                             JOIN users ON sessions.user_id = users.id
                            GROUP BY user_id, date
                           HAVING COUNT(*) > 1)
           AND date IN (SELECT date
                          FROM sessions
                          JOIN users ON sessions.user_id = users.id
                         GROUP BY user_id, date
                        HAVING COUNT(*) > 1);''')
