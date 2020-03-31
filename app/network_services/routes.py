from os import makedirs
from os.path import join
from flask import render_template, flash, redirect, url_for, request, abort
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from app.network_services import bp
from .forms import NewNsForm, EditNsForm, BaseNsForm
from app.models import NetworkService, VnfdPackage
from app import db
from Helper import Log, Action, ActionHandler
from config import Config
from typing import Optional, List


def _applyChanges(entity):
    db.session.add(entity)
    db.session.commit()


def _assignBaseFormData(form: BaseNsForm, service: NetworkService, vimLocation: str = None):
    service.name = form.name.data
    service.description = form.description.data
    service.is_public = (form.public.data == 'Public')
    if vimLocation is not None:
        service.vim_location = vimLocation
    _applyChanges(service)


def _store(file, path: List[str]) -> str:
    baseFolder, subFolder, entityId = path
    filename = secure_filename(file.filename)
    baseFolder = join(Config.UPLOAD_FOLDER, baseFolder, subFolder)
    makedirs(join(baseFolder, entityId), mode=0o755, exist_ok=True)
    savePath = join(baseFolder, entityId, filename)
    file.save(savePath)
    Log.D(f'Saved file {file.filename} in {savePath}')
    return filename


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/repository', methods=['GET', 'POST'])
@login_required
def repository():
    return render_template('network_services/repository.html', title='Network Services',
                           nss=current_user.NetworkServices)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = NewNsForm()
    if form.validate_on_submit():
        newNs = NetworkService(author=current_user)
        _assignBaseFormData(form, newNs, vimLocation="Main DC")  # Assign using default location

        return redirect(url_for('NetworkServices.edit', nsid=newNs.id))

    return render_template('network_services/create.html', title='New Network Service', form=form)


@bp.route('/edit/<int:nsid>', methods=['GET', 'POST'])
@login_required
def edit(nsid: int):
    def _checkFile(name, message):
        file = request.files.get(name, None)
        if file is None or file.filename == '':
            flash(message, 'error')
            return None
        return file

    def _getButton(request, form):
        buttonNames = ['update', 'updateLocation', 'preloadVnfd',
                       'preloadVim', 'onboardVim', 'deleteVim',
                       'preloadNsd', 'onboardNsd', 'deleteNsd',
                       'closeAction', 'cancelAction']

        for name in buttonNames:
            if form.data[name]:
                return name, None

        choices = ['onboardVnf', 'deleteVnf']
        for key in request.form.keys():
            for choice in choices:
                if choice in key:
                    return choice, int(key.replace(choice, ''))
        return None, None

    def _checkNotBusy():
        if ActionHandler.Get(service.id) is not None:
            flash("Cannot perform multiple actions", 'error')
            return False
        return True

    service = NetworkService.query.get(nsid)
    if service is None:
        abort(404)
    if service.user_id is not current_user.id:
        flash(f"Forbidden - You don't have permission to access this network service", 'error')
        return redirect(url_for('NetworkServices.repository'))

    if request.method == "POST":
        form = EditNsForm()
        if form.validate_on_submit():
            button, identifier = _getButton(request, form)

            if button == 'update':
                _assignBaseFormData(form, service)
                flash("Network Service information updated.")

            elif button == 'preloadVnfd':
                file = _checkFile('fileVnfd', "VNFD file is missing")
                if file is not None:
                    newVnfd = VnfdPackage(network_service=service)
                    _applyChanges(newVnfd)
                    newVnfd.vnfd_file = _store(file, newVnfd.VnfdLocalPath)
                    _applyChanges(newVnfd)
                    flash(f"Pre-loaded new VNFD package: {newVnfd.vnfd_file}")

            elif button == 'updateLocation':
                service.vim_location = form.location.data
                _applyChanges(service)
                flash(f"VIM location set to {service.vim_location}.")

            elif button == 'preloadVim':
                file = _checkFile('fileVim', "VIM image file is missing")
                if file is not None:
                    service.vim_image = _store(file, service.VimLocalPath)
                    _applyChanges(service)
                    flash(f"Pre-loaded VIM image: {service.vim_image}")

            elif button == 'preloadNsd':
                file = _checkFile('fileNsd', "NSD file is missing")
                if file is not None:
                    service.nsd_file = _store(file, service.NsdLocalPath)
                    _applyChanges(service)
                    flash(f"Pre-loaded NSD file: {service.nsd_file}")

            # Asynchronous actions
            elif button in ['closeAction', 'cancelAction']:
                action = ActionHandler.Get(service.id)
                if action is not None:
                    if not action.hasFinished:
                        # TODO: Handle cancel
                        flash("Cancelled action")
                    elif not action.hasFailed:  # In case of error simply remove the action
                        result = action.result
                        if 'Nsd' in action.type:
                            if 'onboard' in action.type:
                                service.nsd_id = result
                            else:
                                service.nsd_id = service.nsd_file = None
                        elif 'Vim' in action.type:
                            if 'onboard' in action.type:
                                service.vim_id = result
                            else:
                                service.vim_id = service.vim_image = None
                        else:
                            vnfd = action.vnfd
                            if vnfd is not None:
                                if 'onboard' in action.type:
                                    vnfd.vnfd_id = result
                                    _applyChanges(vnfd)
                                else:
                                    db.session.delete(vnfd)
                                    db.session.commit()
                        _applyChanges(service)
                    ActionHandler.Delete(service.id)

            elif button in ['onboardVim', 'deleteVim', 'onboardNsd', 'deleteNsd'] or identifier is not None:
                action = button
                if _checkNotBusy():
                    if identifier is not None:
                        vnfd = VnfdPackage.query.get(identifier)
                        if vnfd is not None:
                            _handleActions(action, service, vnfd)
                        else:
                            flash(f"Vnfd package (Id: {identifier}) not found", "error")
                    else:
                        _handleActions(action, service, None)

    form = EditNsForm(
        name=service.name,
        description=service.description,
        public='Public' if service.is_public else 'Private',
        location=service.vim_location
    )

    action = ActionHandler.Get(service.id)

    return render_template('network_services/edit.html', Title=f'Network Service: {service.name}',
                           form=form, service=service, action=action)


def _handleActions(action: str, service: NetworkService, vnfd: Optional[VnfdPackage]):
    def _alreadyExist(type, value):
        if value is not None:
            flash(f'{type} already onboarded with Id: {value}', "error")
            return True
        return False

    def _notify(action, type, value):
        flash(f'{action} {type} with Id: {value}', "info")

    def _launchInBackground(s, t, v):
        bgAction = Action(s, t, v)
        ActionHandler.Set(s.id, bgAction)
        bgAction.Start()

    if 'onboard' in action:
        if 'Vnf' in action:
            if not _alreadyExist("VNFD package", vnfd.vnfd_id):
                _launchInBackground(service, "onboardVnf", vnfd)
                _notify("Onboarding", "VNFD package", vnfd.vnfd_id)
        else:
            _launchInBackground(service, action, None)
            _notify("Onboarding", "VIM image" if 'Vim' in action else "NSD file",
                    service.vim_id if 'Vim' in action else service.nsd_id)

    elif 'delete' in action:
        _launchInBackground(service, action, None)
        if 'Vnf' in action:
            _launchInBackground(service, action, vnfd)
            flash(f'Deleting VNFD {vnfd.id}: {vnfd.vnfd_file} ({vnfd.vnfd_id or "No ID"})')
        else:
            _launchInBackground(service, action, None)
            if 'Vim' in action:
                flash(f'Deleting VIM image: {service.vim_image}')
            else:
                flash(f'Deleting NSD file: {service.nsd_file} ({service.nsd_id or "No ID"})')
