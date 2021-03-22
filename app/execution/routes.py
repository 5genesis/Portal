from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from typing import Dict
from app import db
from app.execution import bp
from app.models import Experiment, Execution
from Helper import Config, LogInfo, Log
from REST import DispatcherApi, ElcmApi, AnalyticsApi


@bp.route('/<executionId>', methods=['GET'])
@login_required
def execution(executionId: int):
    def _responseToLogList(response):
        return [LogInfo(response["PreRun"]), LogInfo(response["Executor"]), LogInfo(response["PostRun"])]

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
                localResponse: Dict = DispatcherApi().GetExecutionLogs(executionId, current_user)
                Log.D(f'Access execution logs response {localResponse}')
                status = localResponse["Status"]
                if status == 'Success':
                    localLogs = _responseToLogList(localResponse)
                    remoteLogs = None
                    analyticsUrl = AnalyticsApi().GetUrl(experiment.id, current_user)

                    if experiment.remoteDescriptor is not None:
                        success = False
                        peerId = ElcmApi().GetPeerId(executionId)
                        if peerId is not None:
                            remote = Config().EastWest.RemoteApi(experiment.remotePlatform)
                            if remote is not None:
                                try:
                                    remoteResponse = remote.GetExecutionLogs(peerId)
                                    if remoteResponse['Status'] == 'Success':
                                        remoteLogs = _responseToLogList(remoteResponse)
                                        success = True
                                except Exception: pass
                        if not success:
                            flash('Could not retrieve remote execution logs', 'warning')

                    return render_template('execution/execution.html', title=f'Execution {execution.id}',
                                           execution=execution, localLogs=localLogs, remoteLogs=remoteLogs,
                                           experiment=experiment, grafanaUrl=config.GrafanaUrl,
                                           executionId=getLastExecution() + 1,
                                           dispatcherUrl=config.ELCM.Url, analyticsUrl=analyticsUrl,
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
