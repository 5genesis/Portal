from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_required
from app.network_services import bp
from .forms import NewNsForm, EditNsForm
from app.models import NetworkService
from app import db
from Helper import ActionHandler
from .edit_handler import EditHandler


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
        EditHandler.AssignBaseFormData(db, form, newNs, vimLocation="Main DC")  # Assign using default location
        return redirect(url_for('NetworkServices.edit', nsid=newNs.id))

    return render_template('network_services/create.html', title='New Network Service', form=form)


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

        if form.validate_on_submit():
            handler = EditHandler(request, form, service, db)
            handler.Handle()

    form = EditNsForm(
        name=service.name,
        description=service.description,
        public='Public' if service.is_public else 'Private',
        location=service.vim_location
    )

    action = ActionHandler.Get(service.id)

    return render_template('network_services/edit.html', Title=f'Network Service: {service.name}',
                           form=form, service=service, action=action)


