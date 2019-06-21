from datetime import datetime, timedelta
from secrets import token_urlsafe

from werkzeug.security import check_password_hash, generate_password_hash

from app import db

class User(db.Model):
    """Object relational model of users"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=True, nullable=False)
    access_token = db.Column(db.String(128))
    token_expiry = db.Column(db.DateTime)

    def __repr__(self):
        return f"User(username='{self.username}')"

    def set_password(self, password):
        """Set a password for a user"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Assert whether a given password matches the hash of the stored password"""
        return check_password_hash(self.password_hash, password)

    def set_token(self, expires_in=900):
        self.access_token = token_urlsafe()
        self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
