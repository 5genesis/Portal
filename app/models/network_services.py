from app import db
from Helper import ActionHandler


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
    vnfdRelation = db.relationship('VnfdPackage', backref='network_service', lazy='dynamic')

    @property
    def Busy(self):
        return ActionHandler.Get(self.id) is not None

    @property
    def VNFDs(self):
        return list(VnfdPackage.query.filter_by(service_id=self.id).order_by(VnfdPackage.id.desc()))

    @property
    def VimLocalPath(self):
        return ['network_services', 'vim', str(self.id)]

    @property
    def NsdLocalPath(self):
        return ['network_services', 'nsd', str(self.id)]

    @property
    def Ready(self):
        return self.vim_location is not None and self.vim_id is not None and \
            self.nsd_id is not None and \
            len(self.VNFDs) != 0 and all([vnf.Ready for vnf in self.VNFDs])


class VnfdPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('network_service.id'))
    vnfd_file = db.Column(db.String(256))
    vnfd_id = db.Column(db.String(256))

    @property
    def VnfdLocalPath(self):
        return ['network_services', 'vnfd', str(self.id)]

    @property
    def Ready(self):
        return self.vnfd_id is not None
