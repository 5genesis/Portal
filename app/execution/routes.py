from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from typing import Dict
from app import db
from app.execution import bp
from app.models import Experiment, Execution
from Helper import Config, LogInfo, Log
from REST import ElcmApi


@bp.route('/<executionId>/reloadLog', methods=['GET'])
@bp.route('/<executionId>', methods=['GET'])
@login_required
def execution(executionId: int):
    exe: Execution = Execution.query.get(executionId)
    if exe is None:
        Log.I(f'Execution not found')
        flash(f'Execution not found', 'error')
        return redirect(url_for('main.index'))

    else:
        exp: Experiment = Experiment.query.get(exe.experiment_id)
        if exp.user_id is current_user.id:
            try:
                # Get Execution logs information
                config = Config()
                jsonResponse: Dict = ElcmApi().GetLogs(executionId)
                Log.D(f'Access execution logs response {jsonResponse}')
                status = jsonResponse["Status"]
                if status == 'Not Found':
                    Log.I(f'Execution not found')
                    flash(f'Execution not found', 'error')
                    return redirect(url_for('main.index'))

                else:
                    executor = LogInfo(jsonResponse["Executor"])
                    postRun = LogInfo(jsonResponse["PostRun"])
                    preRun = LogInfo(jsonResponse["PreRun"])
                    return render_template('execution/execution.html', title='execution', execution=exe,
                                           executor=executor, postRun=postRun, preRun=preRun, experiment=exp,
                                           grafanaUrl=config.GrafanaUrl, executionId=getLastExecution() + 1,
                                           dispatcherUrl=config.Dispatcher.Url)
            except Exception as e:
                Log.E(f'Error accessing execution{exe.experiment_id}: {e}')
                flash(f'Exception while trying to connect with dispatcher: {e}', 'error')
                return redirect(f"experiment/{exe.experiment_id}")
        else:
            Log.I(f'Forbidden - User {current_user.name} don\'t have permission to access execution{executionId}')
            flash(f'Forbidden - You don\'t have permission to access this execution', 'error')
            return redirect(url_for('main.index'))


def getLastExecution() -> int:
    return db.session.query(Execution).order_by(Execution.id.desc()).first().id
