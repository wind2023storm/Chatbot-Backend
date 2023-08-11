import os
from . import db
from flask_login import UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
import uuid
from sqlalchemy.dialects.postgresql import UUID
from time import time
from datetime import datetime

class Chat(UserMixin, db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    model = db.Column(db.String(255))
    conversation = db.Column(db.String(255))
    creativity = db.Column(db.Float)
    behavior = db.Column(db.String(700))
    behaviormodel = db.Column(db.String(255))
    rider_level = db.Column(db.String(255))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(255))
    location = db.Column(db.String(700))
    create_date = db.Column(db.Date, default=datetime.utcnow)
    update_date = db.Column(
        db.Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)

    def __repr__(self):
        return f'Chat {self.label}'

    @staticmethod
    def get_chat(label, description):
        return Chat.query.filter_by(label=label, description=description).first()

class Message(UserMixin, db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.JSON)
    behavior = db.Column(db.String(255))
    name = db.Column(db.String(255))
    creativity = db.Column(db.Float)
    create_date = db.Column(db.Date, default=datetime.utcnow)
    update_date = db.Column(
        db.Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)

    def __repr__(self):
        return f'message {self.id}'

    @staticmethod
    def get_message(chat_id):
        return Message.query.filter_by(chat_id=chat_id).first()