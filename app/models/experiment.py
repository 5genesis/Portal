from typing import Dict, List
from app import db
from .json_encoded_dict import JSONEncodedDict
from .execution import Execution
from Helper import Config


experiment_ns = db.Table('experiments_ns',
                         db.Column('experiment_id', db.Integer, db.ForeignKey('experiment.id')),
                         db.Column('ns_id', db.Integer, db.ForeignKey('network_service.id'))
                         )


class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(16))
    automated = db.Column(db.Boolean)
    reservation_time = db.Column(db.Integer)
    test_cases = db.Column(JSONEncodedDict)
    ues = db.Column(JSONEncodedDict)
    slice = db.Column(db.String(64))
    scenario = db.Column(db.String(64))
    exclusive = db.Column(db.Boolean)
    application = db.Column(db.String(64))
    parameters = db.Column(JSONEncodedDict)
    executions = db.relationship('Execution', backref='experiment', lazy='dynamic')
    networkServicesRelation = db.relationship('NetworkService', secondary=experiment_ns)
    remotePlatform = db.Column(db.String(128))
    remoteDescriptor_id = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    remoteDescriptor = db.relationship('Experiment', remote_side=[id], backref='parentDescriptor')
    remoteNetworkServices = db.Column(JSONEncodedDict)

    def __repr__(self):
        return f'<Id: {self.id}, Name: {self.name}, User_id: {self.user_id}, Type: {self.type}, ' \
            f'Unattended: {self.automated}, TestCases: {self.test_cases}, Slice: {self.slice}>'

    def experimentExecutions(self) -> List:
        exp: db.BaseQuery = Execution.query.filter_by(experiment_id=self.id)
        return list(exp.order_by(Execution.id.desc()))

    def _remoteInfo(self):
        if self.type == 'RemoteSide':
            return {'Remote': Config().Platform}
        else:
            return {
                'Remote': self.remotePlatform,
                'RemoteDescriptor': self.remoteDescriptor.serialization() if self.remoteDescriptor is not None else None
            }

    def _nsInfo(self):
        if self.type == 'RemoteSide':
            nss = self.remoteNetworkServices or []
        else:
            nss = [(ns.nsd_id, ns.vim_location) for ns in self.networkServicesRelation]

        return {
            'Slice': self.slice,
            'Scenario': self.scenario,
            'NSs': nss
        }

    def serialization(self) -> Dict[str, object]:
        descriptor = {
            'ExperimentType': 'Distributed' if self.type == 'RemoteSide' else self.type,
            'Automated': self.automated,
            'TestCases': self.test_cases,
            'UEs': self.ues,

            'ExclusiveExecution': self.exclusive,
            'ReservationTime': self.reservation_time,

            'Application': self.application,
            'Parameters': self.parameters,

            'Version': '2.1.0',
            'Extra': {}
        }

        descriptor.update(self._remoteInfo())
        descriptor.update(self._nsInfo())

        return descriptor
