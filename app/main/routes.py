from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from REST import Dispatcher_Api
from app import db
from app.main import bp
from app.models import User, Experiment, Execution, Action, VNF
from app.main.forms import ExperimentForm, RunExperimentForm
from Helper import Config, LogInfo
from datetime import datetime


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    experiments = current_user.user_experiments()
    formRun = RunExperimentForm()
    config = Config()
    notices = config.Notices
    if formRun.validate_on_submit():
        try:
            api = Dispatcher_Api(config.Dispatcher.Host, config.Dispatcher.Port, "/api/v0")  # //api/v0
            jsonresponse = api.Post(request.form['id'])
            flash(f'Success: {jsonresponse["Success"]} - Execution Id: '
                  f'{jsonresponse["ExecutionId"]} - Message: {jsonresponse["Message"]}', 'info')
            execution = Execution(id=jsonresponse["ExecutionId"], experiment_id=request.form['id'], status='Init')
            db.session.add(execution)
            db.session.commit()
            exp = Experiment.query.get(execution.experiment_id)
            action = Action(timestamp=datetime.utcnow(), author=current_user,
                            message=f'<a href="/execution/{execution.id}">Ran experiment: {exp.name}</a>')
            db.session.add(action)
            db.session.commit()
        except Exception as e:
            flash(f'Exception while trying to connect with dispatcher: {e}', 'error')
        return redirect(url_for('main.index'))
    actions = User.query.get(current_user.id).user_actions()
    return render_template('index.html', title='Home', formRun=formRun, experiments=experiments, notices=notices,
                           actions=actions)


@bp.route('/new_experiment', methods=['GET', 'POST'])
@login_required
def new_experiment():
    list_UEs = list(Config().UEs.keys())
    form = ExperimentForm()
    if form.validate_on_submit():
        test_cases_selected = request.form.getlist('test_cases')
        ues_selected = request.form.getlist('ues')
        if not test_cases_selected:
            flash(f'Please, select at least one Test Case', 'error')
            return redirect(url_for('main.new_experiment'))
        experiment = Experiment(name=form.name.data, author=current_user, unattended=True, type=form.type.data,
                                test_cases=test_cases_selected, ues=ues_selected)
        db.session.add(experiment)
        db.session.commit()
        action = Action(timestamp=datetime.utcnow(), author=current_user,
                        message=f'<a href="/experiment/{experiment.id}">Created experiment: {form.name.data}</a>')
        db.session.add(action)
        db.session.commit()
        flash('Your experiment has been successfully created', 'info')
        return redirect(url_for('main.index'))
    return render_template('new_experiment.html', title='Home', form=form,
                           test_case_list=Config().TestCases, ue_list=list_UEs)


@bp.route('/experiment/<experiment_id>', methods=['GET', 'POST'])
@login_required
def experiment(experiment_id):
    exp = Experiment.query.get(experiment_id)
    if exp is None:
        flash(f'Experiment not found', 'error')
        return redirect(url_for('main.index'))
    else:
        if exp.user_id is current_user.id:
            executions = exp.experiment_executions()
            if executions.count() == 0:
                flash(f'The experiment {exp.name} doesn\'t have any executions yet', 'info')
                return redirect(url_for('main.index'))
            else:
                return render_template('experiment.html', title='Experiment', experiment=exp, executions=executions)
        else:
            flash(f'Forbidden - You don\'t have permission to access this experiment', 'error')
            return redirect(url_for('main.index'))


@bp.route('/execution/<execution_id>', methods=['GET'])
@login_required
def execution(execution_id):
    exe = Execution.query.get(execution_id)
    if exe is None:
        flash(f'Execution not found', 'error')
        return redirect(url_for('main.index'))
    else:
        exp = Experiment.query.get(exe.experiment_id)
        if exp.user_id is current_user.id:
            try:
                config = Config()
                api = Dispatcher_Api(config.Dispatcher.Host, config.Dispatcher.Port, "/experiment")
                jsonresponse = api.Get(execution_id)
                status = jsonresponse["Status"]
                if status == 'Not Found':
                    flash(f'Execution not found', 'error')
                    return redirect(url_for('main.index'))
                else:
                    executor = LogInfo(jsonresponse["Executor"])
                    postRun = LogInfo(jsonresponse["PostRun"])
                    preRun = LogInfo(jsonresponse["PreRun"])
                    return render_template('execution.html', title='Execution', execution=exe, log_status=status,
                                           executor=executor, postRun=postRun, preRun=preRun)
            except Exception as e:
                flash(f'Exception while trying to connect with dispatcher: {e}', 'error')
        else:
            flash(f'Forbidden - You don\'t have permission to access this execution', 'error')
            return redirect(url_for('main.index'))


@bp.route('/vnf_repository', methods=['GET', 'POST'])
@login_required
def vnf_repository():
    VNFs = current_user.user_VNFs()
    return render_template('vnf_repository.html', title='Home', VNFs=VNFs)
