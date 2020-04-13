import json
from datetime import datetime, timezone
from typing import Dict
from flask import request, jsonify
from app import db
from app.api import bp
from app.models import Execution
from app.execution.routes import getLastExecution
from Helper import Log


@bp.route('/execution/<executionId>', methods=['PATCH'])
def setExecutionStatus(executionId: int) -> Dict[str, str]:
    data: Dict = json.loads(request.data.decode('utf8'))
    Log.D(f'ELCM execution data (Execution: {executionId}): {data}')
    execution: Execution = Execution.query.get(int(executionId))
    if execution:
        if 'Status' in data:
            if data["Status"] in ['PreRun']:
                execution.start_time = datetime.now(timezone.utc)
            elif data["Status"] in ['Finished', 'Cancelled', 'Errored']:
                execution.end_time = datetime.now(timezone.utc)

            execution.status = data["Status"]
            Log.I(f'Execution {str(execution.id)}: Status changed to {execution.status}')

        if 'Dashboard' in data:
            execution.dashboard_url = str(data["Dashboard"])
            Log.I(f'Execution {str(execution.id)}: Dasboard URL assigned: {execution.dashboard_url}')

        if 'PerCent' in data:
            execution.percent = data["PerCent"]
            Log.I(f'Execution {str(execution.id)}: Percent - {str(execution.percent)}%')

        if 'Message' in data:
            execution.message = str(data["Message"])
            Log.I(f'Execution {str(execution.id)}: Message - {str(execution.message)}')
        db.session.commit()

    return jsonify({'Status': 'Success'})


@bp.route('/<int:executionId>/json')
def executionJson(executionId: int) -> Dict[str, object]:
    execution: Execution = Execution.query.get(executionId)
    if execution is not None:
        status = execution.status
        percent = execution.percent
        message = execution.message
    else:
        percent = 0
        message = []
        status = 'ERR'
    return jsonify({'Status': status, 'PerCent': percent, 'Message': message})


@bp.route('/nextExecutionId')
def nextExecutionId() -> Dict[str, int]:
    Log.D(f'Next execution ID: {getLastExecution() + 1}')
    return jsonify({'NextId': getLastExecution() + 1})
