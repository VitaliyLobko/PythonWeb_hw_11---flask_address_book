from src import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    token_cookie = db.Column(db.String(255), nullable=True, default=None)
    contacts = relationship('Contact', back_populates='user')

    def __repr__(self):
        return f"User {self.id}. {self.username}, {self.email}"


class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(350), unique=True, nullable=False)
    fullname = db.Column(db.String(350), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(300), nullable=True)
    size = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', cascade='all, delete', back_populates='contacts')

    def __repr__(self):
        return f"Contact({self.id}, {self.fullname}, {self.email},  {self.phone},  {self.path})"
