import os
import shutil
from typing import List
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from config import Config as UploaderConfig
from app import db
from app.models import Action, VNF, NS
from app.ns_management import bp
from app.ns_management.forms import VNFForm, NSForm
from Helper import Log


@bp.route('/repository', methods=['GET', 'POST'])
@login_required
def repository():
    VNFs: List[VNF] = current_user.userVNFs()
    NSs: List[NS] = current_user.userNSs()
    return render_template('ns_management/repository.html', title='Home', VNFs=VNFs, NSs=NSs)


def _store(file, baseFolder, subfolder, entityId) -> str:
    filename = secure_filename(file.filename)
    baseFolder = os.path.join(UploaderConfig.UPLOAD_FOLDER, baseFolder, entityId)
    os.makedirs(os.path.join(baseFolder, subfolder), mode=0o755, exist_ok=True)
    savePath = os.path.join(baseFolder, subfolder, filename)
    file.save(savePath)
    Log.D(f'Saved file {file.filename} in {savePath}')
    return filename


@bp.route('/uploadNs', methods=['GET', 'POST'])
@login_required
def upload_NS():
    form = NSForm()
    if form.validate_on_submit():
        # Check if files were uploaded correctly
        fileNSD = request.files.get('fileNSD', None)
        if fileNSD is None or fileNSD.filename == '':
            Log.I('Can\'t upload NS. There are files missing')
            flash('There are files missing', 'error')
            return redirect(request.url)
        else:
            Log.D(f'Upload NS form data - Name: {form.name.data}, Description: {form.description.data}, '
                  f'NDS {fileNSD.filename}')
            newNs = NS(name=form.name.data, author=current_user, description=form.description.data)
            db.session.add(newNs)
            db.session.commit()

            newNs.NSD = _store(fileNSD, 'nss', 'nsd', str(newNs.id))
            db.session.add(newNs)
            db.session.commit()
            Log.I(f'Saved NS: {str(newNs)}')

            action: Action = Action(timestamp=datetime.utcnow(), author=current_user,
                                    message=f'<a href="/NS/repository">Uploaded NS: {newNs.name}</a>')
            Log.I(f'Added action - Uploaded NS')
            db.session.add(action)
            db.session.commit()

            flash('Your VNF has been successfully uploaded', 'info')
            return redirect(url_for('NsManagement.repository'))

    return render_template('ns_management/upload_ns.html', title='Home', form=form)


@bp.route('/uploadVnf', methods=['GET', 'POST'])
@login_required
def upload_VNF():
    form = VNFForm()
    if form.validate_on_submit():
        fileVNFD = request.files.get('fileVNFD', None)
        fileImage = request.files.get('fileImage', None)

        if fileVNFD is None or fileVNFD.filename == '' \
            or fileImage is None or fileImage.filename == '':
            Log.I('Can\'t upload VNF. There are files missing')
            flash('There are files missing', 'error')
            return redirect(request.url)
        else:
            Log.D(f'Upload VNF form data - Name: {form.name.data}, Description: {form.description.data}, '
                  f'VNFD {fileVNFD.filename}, image: {fileImage.filename}')
            newVnf = VNF(name=form.name.data, author=current_user, description=form.description.data)
            db.session.add(newVnf)
            db.session.commit()

            newVnf.VNFD = _store(fileVNFD, 'vnfs', 'vnfd', str(newVnf.id))
            newVnf.image = _store(fileImage, 'vnfs', 'images', str(newVnf.id))
            db.session.add(newVnf)
            db.session.commit()
            Log.I(f'Saved VNF: {str(newVnf)}')

            action: Action = Action(
                timestamp=datetime.utcnow(), author=current_user,
                message=f'<a href="{url_for("NsManagement.repository")}">Uploaded VNF: {newVnf.name}</a>'
            )
            Log.I(f'Added action - Uploaded VNF')
            db.session.add(action)
            db.session.commit()

            flash('Your VNF has been successfully uploaded', 'info')
            return redirect(url_for('NsManagement.repository'))

    return render_template('ns_management/upload_vnf.html', title='Home', form=form)


@bp.route('/deleteVnf/<vnfId>', methods=['GET'])
@login_required
def deleteVnf(vnfId: int):
    vnf: VNF = VNF.query.get(vnfId)
    if vnf:
        if vnf.user_id == current_user.id:
            db.session.delete(vnf)
            db.session.commit()

            # Remove stored files
            shutil.rmtree(os.path.join(UploaderConfig.UPLOAD_FOLDER, 'vnfs', str(vnfId)))
            Log.I(f'VNF {vnfId} successfully removed')
            flash(f'The VNF has been successfully removed', 'info')

        else:
            Log.I(f'Forbidden - User {current_user.name} don\'t have permission to remove VNF {vnfId}')
            flash(f'Forbidden - You don\'t have permission to remove this VNF', 'error')

    else:
        return render_template('errors/404.html'), 404

    return redirect(url_for('NsManagement.repository'))


@bp.route('/deleteNs/<nsId>', methods=['GET'])
@login_required
def deleteNs(nsId: int):
    ns = NS.query.get(nsId)
    if ns:
        if ns.user_id == current_user.id:
            db.session.delete(ns)
            db.session.commit()

            # Remove stored files
            shutil.rmtree(os.path.join(UploaderConfig.UPLOAD_FOLDER, 'nss', str(nsId)))
            Log.I(f'NS {nsId} successfully removed')
            flash(f'The NS has been successfully removed', 'info')

        else:
            Log.I(f'Forbidden - User {current_user.name} don\'t have permission to remove NS {nsId}')
            flash(f'Forbidden - You don\'t have permission to remove this NS', 'error')

    else:
        return render_template('errors/404.html'), 404

    return redirect(url_for('NsManagement.repository'))
