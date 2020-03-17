from app import db


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
