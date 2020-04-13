from os import makedirs
from os.path import join
from werkzeug.utils import secure_filename
from config import Config
from flask import flash
from flask_login import current_user
from Helper import ActionHandler, Action
from typing import Optional, List
from .forms import BaseNsForm
from app.models import NetworkService, VnfdPackage
from REST import DispatcherApi


class EditHandler:
    buttonNames = ['update', 'preloadVnfd',
                   'preloadVim', 'onboardVim', 'deleteVim',
                   'preloadNsd', 'onboardNsd', 'deleteNsd',
                   'closeAction', 'cancelAction']

    def __init__(self, request, form, service, db, userId):
        self.request = request
        self.service = service
        self.form = form
        self.db = db
        self.userId = userId

    @classmethod
    def ApplyChanges(cls, db, entity):
        db.session.add(entity)
        db.session.commit()

    @classmethod
    def AssignBaseFormData(cls, db, form: BaseNsForm, service: NetworkService):
        service.name = form.name.data
        service.description = form.description.data
        service.is_public = (form.public.data == 'Public')
        cls.ApplyChanges(db, service)

    @classmethod
    def Store(cls, file, path: List[str]) -> str:
        baseFolder, subFolder, entityId = path
        filename = secure_filename(file.filename)
        baseFolder = join(Config.UPLOAD_FOLDER, baseFolder, subFolder)
        makedirs(join(baseFolder, entityId), mode=0o755, exist_ok=True)
        savePath = join(baseFolder, entityId, filename)
        file.save(savePath)
        return filename

    def CheckFile(self, name, message):
        file = self.request.files.get(name, None)
        if file is None or file.filename == '':
            flash(message, 'error')
            return None
        return file

    def GetButton(self):
        if self.form is not None:
            for name in self.buttonNames:
                if self.form.data[name]:
                    return name, None

            choices = ['onboardVnf', 'deleteVnf']
            for key in self.request.form.keys():
                for choice in choices:
                    if choice in key:
                        return choice, int(key.replace(choice, ''))
        return None, None

    def CheckNotBusy(self):
        if self.service.Busy:
            flash("Cannot perform multiple actions", 'error')
            return False
        return True

    def Handle(self):
        button, identifier = self.GetButton()

        if button == 'update':
            self.AssignBaseFormData(self.db, self.form, self.service)
            flash("Network Service information updated.")

        elif button == 'preloadVnfd':
            file = self.CheckFile('fileVnfd', "VNFD file is missing")
            if file is not None:
                newVnfd = VnfdPackage(network_service=self.service)
                self.ApplyChanges(self.db, newVnfd)
                newVnfd.vnfd_file = self.Store(file, newVnfd.VnfdLocalPath)
                self.ApplyChanges(self.db, newVnfd)
                flash(f"Pre-loaded new VNFD package: {newVnfd.vnfd_file}")

        elif button == 'preloadVim':
            file = self.CheckFile('fileVim', "VIM image file is missing")
            if file is not None:
                self.service.vim_image = self.Store(file, self.service.VimLocalPath)
                self.ApplyChanges(self.db, self.service)
                flash(f"Pre-loaded VIM image: {self.service.vim_image}")

        elif button == 'preloadNsd':
            file = self.CheckFile('fileNsd', "NSD file is missing")
            if file is not None:
                self.service.nsd_file = self.Store(file, self.service.NsdLocalPath)
                self.ApplyChanges(self.db, self.service)
                flash(f"Pre-loaded NSD file: {self.service.nsd_file}")

        # Asynchronous actions
        elif button in ['closeAction', 'cancelAction']:
            action = ActionHandler.Get(self.service.id)
            if action is not None:
                if not action.hasFinished:
                    # TODO: Handle cancel
                    flash("Cancelled action")
                elif not action.hasFailed:  # In case of error simply remove the action
                    result = action.result
                    if 'Nsd' in action.type:
                        if 'onboard' in action.type:
                            self.service.nsd_id = result
                        else:
                            self.service.nsd_id = self.service.nsd_file = None
                    elif 'Vim' in action.type:
                        if 'onboard' in action.type:
                            self.service.vim_id = result
                        else:
                            self.service.vim_id = self.service.vim_image = None
                    else:
                        vnfd = action.vnfd
                        if vnfd is not None:
                            if 'onboard' in action.type:
                                vnfd.vnfd_id = result
                                self.ApplyChanges(self.db, vnfd)
                            else:
                                self.db.session.delete(vnfd)
                                self.db.session.commit()
                    self.ApplyChanges(self.db, self.service)
                ActionHandler.Delete(self.service.id)

        elif button in ['onboardVim', 'deleteVim', 'onboardNsd', 'deleteNsd'] or identifier is not None:
            action = button
            if self.CheckNotBusy():
                if identifier is not None:
                    vnfd = VnfdPackage.query.get(identifier)
                    if vnfd is not None:
                        self.CreateNewAction(action, vnfd)
                    else:
                        flash(f"Vnfd package (Id: {identifier}) not found", "error")
                else:
                    self.CreateNewAction(action, None)

    def CreateNewAction(self, action: str, vnfd: Optional[VnfdPackage]):
        def _alreadyExist(type, value):
            if value is not None:
                flash(f'{type} already onboarded with Id: {value}', "error")
                return True
            return False

        def _notify(action, type, value):
            flash(f'{action} {type} with Id: {value}', "info")

        def _launchInBackground(t, v):
            DispatcherApi().RenewUserTokenIfExpired(current_user)
            token = current_user.CurrentDispatcherToken

            bgAction = Action(self.service, t, v, token)
            ActionHandler.Set(self.service.id, bgAction)
            bgAction.Start()

        if 'onboard' in action:
            if 'Vnf' in action:
                if not _alreadyExist("VNFD package", vnfd.vnfd_id):
                    _launchInBackground("onboardVnf", vnfd)
                    _notify("Onboarding", "VNFD package", vnfd.vnfd_id)
            else:
                # Ensure that the launched action finds the correct location
                if "Vim" in action and self.service.vim_location is None:
                    self.service.vim_location = self.request.form['location']
                    self.ApplyChanges(self.db, self.service)
                _launchInBackground(action, None)
                _notify("Onboarding", "VIM image" if 'Vim' in action else "NSD file",
                        self.service.vim_id if 'Vim' in action else self.service.nsd_id)

        elif 'delete' in action:
            _launchInBackground(action, None)
            if 'Vnf' in action:
                _launchInBackground(action, vnfd)
                flash(f'Deleting VNFD {vnfd.id}: {vnfd.vnfd_file} ({vnfd.vnfd_id or "No ID"})')
            else:
                _launchInBackground(action, None)
                if 'Vim' in action:
                    flash(f'Deleting VIM image: {self.service.vim_image}')
                else:
                    flash(f'Deleting NSD file: {self.service.nsd_file} ({self.service.nsd_id or "No ID"})')
