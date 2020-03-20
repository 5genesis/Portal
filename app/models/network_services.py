from app import db


class NetworkService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(64))
    description = db.Column(db.String(256))
    is_public = db.Column(db.Boolean)
    vim_image = db.Column(db.String(256))
    vim_location = db.Column(db.String(64))
    vim_id = db.Column(db.String(256))  # Probably not an ID, but a value to signal it has been onboarded
    nsd_file = db.Column(db.String(256))
    nsd_id = db.Column(db.String(256))
    current_onboard = db.Column(db.Integer, db.ForeignKey('onboard_status.id'))
    vnfdRelation = db.relationship('VnfdPackage', backref='network_service', lazy='dynamic')

    @property
    def VNFDs(self):
        return list(VnfdPackage.query.filter_by(service_id=self.id).order_by(VnfdPackage.id.desc()))


class VnfdPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('network_service.id'))
    vnfd_file = db.Column(db.String(256))
    vnfd_id = db.Column(db.String(256))


class OnboardStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(32))
    entity_id = db.Column(db.Integer)
    status = db.Column(db.String(256))
    finished = db.Column(db.Boolean)
