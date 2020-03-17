import jwt
from typing import Dict, List
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from .experiment import Experiment
from .network_services import NetworkService


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    organization = db.Column(db.String(32))
    token = db.Column(db.String(512))
    tokenTimestamp = db.Column(db.DATETIME)
    experimentsRelation = db.relationship('Experiment', backref='author', lazy='dynamic')
    actionsRelation = db.relationship('Action', backref='author', lazy='dynamic')
    networkServiceRelation = db.relationship('NetworkService', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<Id: {self.id}, Username: {self.username}, Email: {self.email}, Organization: {self.organization}'

    def setPassword(self, password):
        self.password_hash = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.password_hash, password)

    def getResetPasswordToken(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @property
    def CurrentDispatcherToken(self):
        return self.token

    @property
    def Experiments(self) -> List:
        return Experiment.query.filter_by(user_id=self.id).order_by(Experiment.id.desc())

    @property
    def Actions(self) -> List:
        return Action.query.filter_by(user_id=self.id).order_by(Action.id.desc()).limit(10)

    @property
    def NetworkServices(self) -> List:
        return NetworkService.query.filter_by(user_id=self.id).order_by(NetworkService.name.asc())

    @staticmethod
    def verifyResetPasswordToken(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
            return User.query.get(id)
        except:
            return None

    def serialization(self) -> Dict[str, object]:
        experimentIds: List[int] = [exp.id for exp in self.Experiments]
        dictionary = {'Id': self.id, 'UserName': self.username, 'Email': self.email, 'Organization': self.organization,
                      'Experiments': experimentIds}
        return dictionary


@login.user_loader
def load_user(id: int) -> User:
    return User.query.get(int(id))


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DATETIME)
    message = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Id: {self.id}, Timestamp: {self.timestamp}, Message: {self.message}, ' \
            f'User_id: {self.user_id}>'
