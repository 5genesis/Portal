from typing import List
from flask import render_template, redirect, request
from flask_login import current_user, login_required
from app.main import bp
from app.models import User, Experiment, Action
from app.experiment.forms import RunExperimentForm
from app.experiment.routes import runExperiment
from Helper import Config


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index/reload', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    config = Config()
    notices: List[str] = config.Notices
    actions: List[Action] = User.query.get(current_user.id).userActions()
    experiments: List[Experiment] = current_user.userExperiments()
    formRun = RunExperimentForm()
    if formRun.validate_on_submit():
        runExperiment(config)
        return redirect(f"{request.url}/reload")

    return render_template('index.html', title='Home', formRun=formRun, experiments=experiments, notices=notices,
                           actions=actions)


@bp.route('/info')
def info():
    return render_template('info.html', title="Testbed Info")
