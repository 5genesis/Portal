from os import makedirs
from os.path import join
from flask import render_template, flash, redirect, url_for, request, abort
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from app.network_services import bp
from .forms import NewNsForm, EditNsForm, BaseNsForm
from app.models import NetworkService, VnfdPackage
from app import db
from Helper import Log
from config import Config


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


def _store(file, baseFolder, subfolder, entityId) -> str:
    filename = secure_filename(file.filename)
    baseFolder = join(Config.UPLOAD_FOLDER, baseFolder, entityId)
    makedirs(join(baseFolder, subfolder), mode=0o755, exist_ok=True)
    savePath = join(baseFolder, subfolder, filename)
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

    def _checkDynamicButtons(request):
        choices = ['onboardVnf', 'deleteVnf']
        for key in request.form.keys():
            for choice in choices:
                if choice in key:
                    return choice, int(key.replace(choice, ''))
        return None, None


    service = NetworkService.query.get(nsid)
    if service is None:
        abort(404)
    if service.user_id is not current_user.id:
        flash(f"Forbidden - You don't have permission to access this network service", 'error')
        return redirect(url_for('NetworkServices.repository'))

    if request.method == "POST":
        form = EditNsForm()
        if form.validate_on_submit():
            if form.data['update']:
                _assignBaseFormData(form, service)
                flash("Network Service information updated.")

            elif form.data['preloadVnfd']:
                file = _checkFile('fileVnfd', "VNFD file is missing")
                if file is not None:
                    newVnfd = VnfdPackage(network_service=service)
                    _applyChanges(newVnfd)
                    newVnfd.vnfd_file = _store(file, 'network_services', 'vnfd', str(newVnfd.id))
                    _applyChanges(newVnfd)
                    flash(f"Pre-loaded new VNFD package: {newVnfd.vnfd_file}")

            elif form.data['updateLocation']:
                service.vim_location = form.location.data
                _applyChanges(service)
                flash(f"VIM location set to {service.vim_location}.")

            elif form.data['preloadVim']:
                file = _checkFile('fileVim', "VIM image file is missing")
                if file is not None:
                    service.vim_image = _store(file, 'network_services', 'vim', str(service.id))
                    _applyChanges(service)
                    flash(f"Pre-loaded VIM image: {service.vim_image}")

            elif form.data['preloadNsd']:
                file = _checkFile('fileNsd', "NSD file is missing")
                if file is not None:
                    service.nsd_file = _store(file, 'network_services', 'nsd', str(service.id))
                    _applyChanges(service)
                    flash(f"Pre-loaded NSD file: {service.nsd_file}")

            else:  # Check VNFD buttons
                action, vnfdId = _checkDynamicButtons(request)
                if action is 'onboardVnf':
                    flash(f'Onboard {vnfdId}')
                elif action is 'deleteVnf':
                    flash(f'Delete {vnfdId}')

    form = EditNsForm(
        name=service.name,
        description=service.description,
        public='Public' if service.is_public else 'Private',
        location=service.vim_location
    )

    return render_template('network_services/edit.html', Title=f'Network Service: {service.name}',
                           form=form, service=service)