import jwt
import json
from typing import Dict, List
from time import time
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.types import TypeDecorator, VARCHAR
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from Helper import Config as HelperConfig


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""

    @property
    def python_type(self):
        pass

    def process_literal_param(self, value, dialect):
        pass

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    organization = db.Column(db.String(32))
    token = db.Column(db.String(512))
    tokenTimestamp = db.Column(db.DATETIME)
    experiments = db.relationship('Experiment', backref='author', lazy='dynamic')
    actions = db.relationship('Action', backref='author', lazy='dynamic')
    VNFs = db.relationship('VNF', backref='author', lazy='dynamic')
    NSs = db.relationship('NS', backref='author', lazy='dynamic')

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

    def getCurrentDispatcherToken(self):
        return self.token

    def userExperiments(self) -> List:
        exp: List = Experiment.query.filter_by(user_id=self.id)
        return exp.order_by(Experiment.id.desc())

    def userActions(self) -> List:
        acts: List = Action.query.filter_by(user_id=self.id).order_by(Action.id.desc()).limit(10)
        return acts

    def userVNFs(self) -> List:
        VNFs: List = VNF.query.filter_by(user_id=self.id).order_by(VNF.id)
        return VNFs

    def userNSs(self) -> List:
        NSs: List = NS.query.filter_by(user_id=self.id).order_by(NS.id)
        return NSs

    @staticmethod
    def verifyResetPasswordToken(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def serialization(self) -> Dict[str, object]:
        experimentIds: List[int] = [exp.id for exp in self.userExperiments()]
        dictionary = {'Id': self.id, 'UserName': self.username, 'Email': self.email, 'Organization': self.organization,
                      'Experiments': experimentIds}
        return dictionary


@login.user_loader
def load_user(id: int) -> User:
    return User.query.get(int(id))


experiment_ns = db.Table('experiments_ns',
                         db.Column('experiment_id', db.Integer, db.ForeignKey('experiment.id')),
                         db.Column('ns_id', db.Integer, db.ForeignKey('NS.id'))
                         )


class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(16))
    unattended = db.Column(db.Boolean)
    test_cases = db.Column(JSONEncodedDict)
    ues = db.Column(JSONEncodedDict)
    NSD = db.Column(db.String(256))
    slice = db.Column(db.String(64))
    executions = db.relationship('Execution', backref='experiment', lazy='dynamic')
    network_services = db.relationship('NS', secondary=experiment_ns)

    def __repr__(self):
        return f'<Id: {self.id}, Name: {self.name}, User_id: {self.user_id}, Type: {self.type}, ' \
            f'Unattended: {self.unattended}, TestCases: {self.test_cases}, NSD: {self.NSD}, Slice: {self.slice}>'

    def experimentExecutions(self) -> List:
        exp: db.BaseQuery = Execution.query.filter_by(experiment_id=self.id)
        return list(exp.order_by(Execution.id.desc()))

    def experimentNSs(self) -> List:
        nss: db.BaseQuery = experiment_ns.query.filter_by(experiment_id=self.id)
        return list(nss)

    def serialization(self) -> Dict[str, object]:
        ueDictionary = {}
        allUEs: Dict = HelperConfig().UEs
        executionIds: List = [exe.id for exe in self.experimentExecutions()]

        for ue in self.ues:
            if ue in allUEs.keys(): ueDictionary[ue] = allUEs[ue]

        networkServices = [ns.serialization() for ns in self.network_services]

        dictionary = {'Id': self.id, 'Name': self.name, 'User': User.query.get(self.user_id).serialization(),
                      'Executions': executionIds, "Platform": HelperConfig().Platform,
                      "TestCases": self.test_cases, "UEs": ueDictionary, "Slice": self.slice, "NSD": self.NSD,
                      "NetworkServices": networkServices}
        return dictionary


class Execution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    start_time = db.Column(db.DATETIME)
    end_time = db.Column(db.DATETIME)
    status = db.Column(db.String(32))
    dashboard_url = db.Column(db.String(64))
    percent = db.Column(db.Integer)
    message = db.Column(db.String(128))

    def __repr__(self):
        return f'<Id: {self.id}, Experiment_id: {self.experiment_id}, Start_time: {self.start_time}, ' \
            f'End_time: {self.end_time}, Status: {self.status}, Dashboard_url: {self.dashboard_url}, ' \
            f'Percent: {self.percent}. Message: {self.message} >'


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DATETIME)
    message = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Id: {self.id}, Timestamp: {self.timestamp}, Message: {self.message}, ' \
            f'User_id: {self.user_id}>'


class VNF(db.Model):  # OLD
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(256))
    VNFD = db.Column(db.String(256))
    image = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<VNF: {self.id}, Name: {self.name}, Description: {self.description}, VNFD: {self.VNFD},' \
            f'Image: {self.image}, User_id: {self.user_id}>'

    def serialization(self) -> Dict[str, object]:
        dictionary = {'Id': self.id, 'Name': self.name, 'Description': self.description, 'VNFD': self.VNFD,
                      "Image": self.image, "User": self.user_id}
        return dictionary


class NS(db.Model):  # OLD
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(256))
    NSD = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<NS: {self.id}, Name: {self.name}, Description: {self.description}, NSD: {self.NSD},' \
            f'User_id: {self.user_id}>'

    def serialization(self) -> Dict[str, object]:
        dictionary = {'Id': self.id, 'Name': self.name, 'Description': self.description, 'NSD': self.NSD,
                      "User": self.user_id}
        return dictionary


class NetworkService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(64))
    description = db.Column(db.String(256))
    is_public = db.Column(db.Boolean)
    vim_image = db.Column(db.String(256))
    vim_location = db.Column(db.String(64))
    nsd_file = db.Column(db.String(256))
    nsd_id = db.Column(db.String(256))


class VnfdPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('network_service.id'))
    vnfd_file = db.Column(db.String(256))
    vnfd_id = db.Column(db.String(256))
