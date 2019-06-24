import os

from dotenv import load_dotenv
import sqlalchemy

if __name__ == '__main__':
    basedir = os.path.abspath(os.path.split(os.path.dirname(__file__))[0])
    load_dotenv(os.path.join(basedir, '.env'))
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
    conn = engine.connect()
    conn.execute('DELETE FROM gym_records;')
    conn.execute('DELETE FROM sessions;')
    conn.execute('DELETE FROM exercises;')
    conn.execute('DELETE FROM users;')
