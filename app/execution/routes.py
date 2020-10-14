from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from typing import Dict
from app import db
from app.execution import bp
from app.models import Experiment, Execution
from Helper import Config, LogInfo, Log
from REST import DispatcherApi


@bp.route('/<executionId>/reloadLog', methods=['GET'])
@bp.route('/<executionId>', methods=['GET'])
@login_required
def execution(executionId: int):
    execution: Execution = Execution.query.get(executionId)
    if execution is None:
        Log.I(f'Execution not found')
        flash(f'Execution not found', 'error')
        return redirect(url_for('main.index'))

    else:
        experiment: Experiment = Experiment.query.get(execution.experiment_id)
        if experiment.user_id is current_user.id:
            try:
                # Get Execution logs information
                config = Config()
                jsonResponse: Dict = DispatcherApi().GetExecutionLogs(executionId, current_user)
                Log.D(f'Access execution logs response {jsonResponse}')
                status = jsonResponse["Status"]
                if status == 'Success':
                    executor = LogInfo(jsonResponse["Executor"])
                    postRun = LogInfo(jsonResponse["PostRun"])
                    preRun = LogInfo(jsonResponse["PreRun"])
                    return render_template('execution/execution.html', title=f'Execution {execution.id}',
                                           execution=execution, executor=executor, postRun=postRun, preRun=preRun,
                                           experiment=experiment, grafanaUrl=config.GrafanaUrl,
                                           executionId=getLastExecution() + 1,
                                           dispatcherUrl=config.ELCM.Url,  # TODO: Use dispatcher
                                           ewEnabled=Config().EastWest.Enabled)
                else:
                    if status == 'Not Found':
                        message = "Execution not found"
                    else:
                        message = f"Could not connect with log repository: {status}"
                    Log.I(message)
                    flash(message, 'error')
                    return redirect(url_for('experiment.experiment', experimentId=experiment.id))

            except Exception as e:
                Log.E(f'Error accessing execution{execution.experiment_id}: {e}')
                flash(f'Exception while trying to connect with dispatcher: {e}', 'error')
                return redirect(url_for('experiment.experiment', experimentId=experiment.id))
        else:
            Log.I(f'Forbidden - User {current_user.name} don\'t have permission to access execution{executionId}')
            flash(f'Forbidden - You don\'t have permission to access this execution', 'error')
            return redirect(url_for('main.index'))


def getLastExecution() -> int:
    return db.session.query(Execution).order_by(Execution.id.desc()).first().id
