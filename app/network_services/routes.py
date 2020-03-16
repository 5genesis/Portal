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
from app.network_services import bp
from Helper import Log


@bp.route('/repository', methods=['GET', 'POST'])
@login_required
def repository():
    return render_template('network_services/repository.html', title='Network Services',
                           nss=current_user.NetworkServices)
