from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app.network_services import bp
from .forms import NewNsForm
from app.models import NetworkService, NS
from app import db


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
        name = form.name.data
        description = form.description.data
        isPublic = (form.public.data == 'Public')

        newNs = NetworkService(name=name, description=description, is_public=isPublic, author=current_user)
        db.session.add(newNs)
        db.session.commit()
        flash("Created")

    return render_template('network_services/create.html', title='New Network Service', form=form)
