from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from app import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    activities = db.relationship('Activity', backref='user', lazy=True)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    last_done = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ユーザーIDの追加
    updates = db.relationship('Update', backref='activity', lazy=True, cascade="all, delete-orphan")  

class Update(db.Model):  # *
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.String(500), nullable=True)  # * detail を noteに変更した。
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
