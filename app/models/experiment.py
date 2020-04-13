from typing import Dict, List
from app import db
from Helper import Config as HelperConfig
from .json_encoded_dict import JSONEncodedDict
from .execution import Execution


experiment_ns = db.Table('experiments_ns',
                         db.Column('experiment_id', db.Integer, db.ForeignKey('experiment.id')),
                         db.Column('ns_id', db.Integer, db.ForeignKey('network_service.id'))
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
    networkServicesRelation = db.relationship('NetworkService', secondary=experiment_ns)

    def __repr__(self):
        return f'<Id: {self.id}, Name: {self.name}, User_id: {self.user_id}, Type: {self.type}, ' \
            f'Unattended: {self.unattended}, TestCases: {self.test_cases}, NSD: {self.NSD}, Slice: {self.slice}>'

    def experimentExecutions(self) -> List:
        exp: db.BaseQuery = Execution.query.filter_by(experiment_id=self.id)
        return list(exp.order_by(Execution.id.desc()))

    def serialization(self) -> Dict[str, object]:
        from .user import User

        ueDictionary = {}
        allUEs: Dict = HelperConfig().UEs
        executionIds: List = [exe.id for exe in self.experimentExecutions()]

        for ue in self.ues:
            if ue in allUEs.keys(): ueDictionary[ue] = allUEs[ue]

        # TODO: Update
        networkServices = [] #[ns.serialization() for ns in self.network_services]

        dictionary = {'Id': self.id, 'Name': self.name, 'User': User.query.get(self.user_id).serialization(),
                      'Executions': executionIds, "Platform": HelperConfig().Platform,
                      "TestCases": self.test_cases, "UEs": ueDictionary, "Slice": self.slice, "NSD": self.NSD,
                      "NetworkServices": networkServices}
        return dictionary
