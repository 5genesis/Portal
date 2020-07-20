from datetime import datetime, timezone
from typing import Dict, List, Tuple, Set
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask.json import loads as jsonParse
from flask_login import current_user, login_required
from REST import ElcmApi, DispatcherApi
from app import db
from app.experiment import bp
from app.models import Experiment, Execution, Action, NetworkService
from app.experiment.forms import ExperimentForm, RunExperimentForm
from app.execution.routes import getLastExecution
from Helper import Config, Log, Facility


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    experimentTypes = ['Standard', 'Custom', 'MONROE']

    nss: List[Tuple[str, int]] = []

    # Get User's available NSs
    for ns in current_user.UsableNetworkServices:
         nss.append((ns.name, ns.id))

    form = ExperimentForm()
    if form.validate_on_submit():
        experimentName = request.form.get('name')
        experimentType = request.form.get('type')
        exclusive = (len(request.form.getlist('exclusive')) != 0)

        testCases = request.form.getlist(f'{experimentType}_testCases')
        ues_selected = request.form.getlist(f'{experimentType}_ues')
        scenario = None  # TODO

        parameters = {}
        if experimentType == "Custom":
            for key, value in request.form.items():
                key = str(key)
                if key.endswith('_ParameterTextField') and len(value) != 0:
                    parameters[key.replace('_ParameterTextField', '')] = value
        elif experimentType == "MONROE":
            rawParams = request.form.get('monroeParameters')
            if rawParams is not None:
                rawParams = '{}' if len(rawParams) == 0 else rawParams  # Minimal valid JSON
                try:
                    parameters = jsonParse(rawParams)
                except Exception as e:
                    flash(f'Exception while parsing Parameters: {e}', 'error')
                    return redirect(url_for("experiment.create"))

        automated = (len(request.form.getlist('automate')) != 0) if experimentType == "Custom" else True
        possibleTimes = {'Standard': None,
                         'Custom': None if automated else int(request.form.get('reservationCustom')),
                         'MONROE': int(request.form.get('reservationMonroe'))}
        reservationTime = possibleTimes[experimentType]

        application = request.form.get('application') if experimentType == "MONROE" else None

        experiment = Experiment(
            name=experimentName, author=current_user,
            type=experimentType, exclusive=exclusive,
            test_cases=testCases, ues=ues_selected, scenario=scenario,
            automated=automated, reservation_time=reservationTime,
            parameters=parameters, application=application,
        )

        formSlice = request.form.get('slice', None)

        if formSlice is not None:
            experiment.slice = formSlice

        count = int(request.form.get('nsCount', '0'))
        for i in range(count):
            ns = NetworkService.query.get(request.form[f'NS{i+1}'])
            if ns is not None:
                experiment.networkServicesRelation.append(ns)

        db.session.add(experiment)
        db.session.commit()

        Log.I(f'Added experiment {experiment.id}')

        action: Action = Action(timestamp=datetime.now(timezone.utc), author=current_user,
                                message=f'<a href="/experiment/{experiment.id}">Created experiment: {experimentName}</a>')
        db.session.add(action)
        db.session.commit()
        Log.I(f'Added action - Created experiment')
        flash('Your experiment has been successfully created', 'info')
        return redirect(url_for('main.index'))

    customTestCases = Facility.AvailableCustomTestCases(current_user.email)
    parametersPerTestCase = Facility.TestCaseParameters()
    baseSlices = Facility.BaseSlices()
    scenarios = Facility.Scenarios()
    parameterNamesPerTestCase: Dict[str, Set[str]] = {}
    testCaseNamesPerParameter: Dict[str, Set[str]] = {}
    parameterInfo: Dict[str, Dict[str, str]] = {}
    for testCase in customTestCases:
        parameters = parametersPerTestCase[testCase]
        for parameter in parameters:
            name = parameter['Name']
            parameterInfo[name] = parameter

            if testCase not in parameterNamesPerTestCase.keys():
                parameterNamesPerTestCase[testCase] = set()
            parameterNamesPerTestCase[testCase].add(name)

            if name not in testCaseNamesPerParameter.keys():
                testCaseNamesPerParameter[name] = set()
            testCaseNamesPerParameter[name].add(testCase)

    return render_template('experiment/create.html', title='New Experiment', form=form,
                           standardTestCases=Facility.StandardTestCases(), ues=Facility.UEs(),
                           customTestCases=customTestCases, parameterInfo=parameterInfo,
                           parameterNamesPerTestCase=parameterNamesPerTestCase,
                           testCaseNamesPerParameter=testCaseNamesPerParameter,
                           sliceList=baseSlices, scenarioList=scenarios, nss=nss, experimentTypes=experimentTypes)


@bp.route('/<experimentId>/reload', methods=['GET', 'POST'])
@bp.route('/<experimentId>', methods=['GET', 'POST'])
@login_required
def experiment(experimentId: int):
    config = Config()
    exp: Experiment = Experiment.query.get(experimentId)
    formRun = RunExperimentForm()
    if formRun.validate_on_submit():
        success = runExperiment()
        return redirect(f"{request.url}/reload") if success else redirect(request.url)

    if exp is None:
        Log.I(f'Experiment not found')
        flash(f'Experiment not found', 'error')
        return redirect(url_for('main.index'))

    else:
        if exp.user_id is current_user.id:

            # Get Experiment's executions
            executions: List[Experiment] = exp.experimentExecutions()
            if len(executions) == 0:
                flash(f'The experiment {exp.name} doesn\'t have any executions yet', 'info')
                return redirect(url_for('main.index'))
            else:
                return render_template('experiment/experiment.html', title=f'Experiment: {exp.name}', experiment=exp,
                                       executions=executions, formRun=formRun, grafanaUrl=config.GrafanaUrl,
                                       executionId=getLastExecution() + 1,
                                       dispatcherUrl=config.ELCM.Url)  # TODO: Use dispatcher
        else:
            Log.I(f'Forbidden - User {current_user.name} don\'t have permission to access experiment {experimentId}')
            flash(f'Forbidden - You don\'t have permission to access this experiment', 'error')
            return redirect(url_for('main.index'))


def runExperiment() -> bool:
    """Returns true if no issue has been detected"""
    try:
        jsonResponse: Dict = DispatcherApi().RunCampaign(request.form['id'], current_user)
        success = jsonResponse["Success"]
        message = jsonResponse["Message"]
        executionId = jsonResponse["ExecutionId"]
        if not success:
            raise Exception(message)
        else:
            Log.I(f'Ran experiment {request.form["id"]}')
            Log.D(f'Ran experiment response {jsonResponse}')
            flash(f'Experiment started with Execution Id: {executionId}', 'info')
            execution: Execution = Execution(id=executionId, experiment_id=request.form['id'], status='Init')
            db.session.add(execution)
            db.session.commit()

            Log.I(f'Added execution {jsonResponse["ExecutionId"]}')
            exp: Experiment = Experiment.query.get(execution.experiment_id)
            action = Action(timestamp=datetime.now(timezone.utc), author=current_user,
                            message=f'<a href="/execution/{execution.id}">Ran experiment: {exp.name}</a>')
            db.session.add(action)
            db.session.commit()
            Log.I(f'Added action - Ran experiment')
            return True

    except Exception as e:
        Log.E(f'Error running experiment: {e}')
        flash(f'Exception while trying to connect with dispatcher: {e}', 'error')
        return False


@bp.route('/<experimentId>/descriptor', methods=["GET"])
@login_required
def descriptor(experimentId: int):
    experiment = Experiment.query.get(experimentId)
    if experiment is None:
        flash('Experiment not found', 'error')
        return redirect(url_for('main.index'))
    elif experiment.user_id != current_user.id:
        flash("Forbidden - You don't have permission to access this experiment", 'error')
        return redirect(url_for('main.index'))
    else:
        return jsonify(experiment.serialization())


@bp.route('/kickstart/<experimentId>', methods=["GET"])
def kickstart(experimentId: int):
    try:
        Log.I(f"KS: Kickstarting experiment {experimentId}")
        jsonResponse: Dict = ElcmApi().Run(experimentId)
        execution: Execution = Execution(id=jsonResponse["ExecutionId"], experiment_id=experimentId, status='Init')
        db.session.add(execution)
        db.session.commit()
        Log.I(f'KS: Added execution {jsonResponse["ExecutionId"]}')

        return f'Hush now! Exp {experimentId} - Exec {jsonResponse["ExecutionId"]}'
    except Exception as e:
        return str(e)
