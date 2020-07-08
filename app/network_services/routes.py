from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from app.network_services import bp
from .forms import NewNsForm, EditNsForm
from app.models import NetworkService
from app import db
from Helper import ActionHandler
from .edit_handler import EditHandler
from REST import DispatcherApi, VimInfo
from typing import List


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
        newNs.vim_location = request.form['location']
        EditHandler.AssignBaseFormData(db, form, newNs)
        return redirect(url_for('NetworkServices.edit', nsid=newNs.id))

    locations, error = DispatcherApi().GetVimLocations(current_user)
    if error is not None:
        flash(error, 'error')

    return render_template('network_services/create.html', title='New Network Service', form=form, locations=locations)


@bp.route('/edit/<int:nsid>', methods=['GET', 'POST'])
@login_required
def edit(nsid: int):
    service = NetworkService.query.get(nsid)
    if service is None:
        abort(404)
    if service.user_id is not current_user.id:
        flash(f"Forbidden - You don't have permission to access this network service", 'error')
        return redirect(url_for('NetworkServices.repository'))

    if request.method == "POST":
        form = EditNsForm()

        if form.is_submitted():
            handler = EditHandler(request, form, service, db, current_user.id)
            handler.Handle()
            return redirect(url_for("NetworkServices.edit", nsid=nsid))

    form = EditNsForm(
        name=service.name,
        description=service.description,
        public='Public' if service.is_public else 'Private',
        location=service.vim_location
    )

    action = ActionHandler.Get(service.id)

    images, error = DispatcherApi().GetVimLocationImages(current_user, service.vim_location)
    if error is not None:
        flash(error, 'error')

    return render_template('network_services/edit.html', Title=f'Network Service: {service.name}',
                           form=form, service=service, action=action, images=images)


