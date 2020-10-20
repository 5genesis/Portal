from datetime import datetime, timezone
from typing import Dict, List, Tuple, Set
from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from flask.json import loads as jsonParse
from flask_login import current_user, login_required
from REST import ElcmApi, DispatcherApi
from app import db
from app.experiment import bp
from app.models import Experiment, Execution, Action, NetworkService
from app.experiment.forms import ExperimentForm, RunExperimentForm, DistributedStep1Form, DistributedStep2Form
from app.execution.routes import getLastExecution
from Helper import Config, Log, Facility


def _addSliceInfo(form, experiment):
    maybeSlice = form.get('sliceCheckboxedList', None)
    maybeScenario = form.get('scenarioCheckboxedList', None)

    if maybeSlice is not None:
        experiment.slice = maybeSlice
    if maybeScenario is not None:
        experiment.scenario = maybeScenario

    count = int(form.get('nsCount', '0'))
    for i in range(count):
        ns = NetworkService.query.get(form[f'NS{i + 1}'])
        if ns is not None:
            experiment.networkServicesRelation.append(ns)


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
            test_cases=testCases, ues=ues_selected,
            automated=automated, reservation_time=reservationTime,
            parameters=parameters, application=application,
        )

        if "enableSlicing" in request.form.keys():
            _addSliceInfo(request.form, experiment)

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
                           sliceList=baseSlices, scenarioList=scenarios, nss=nss, experimentTypes=experimentTypes,
                           ewEnabled=Config().EastWest.Enabled)


@bp.route('/create_dist', methods=['GET', 'POST'])
@login_required
def createDist():
    eastWest = Config().EastWest
    if not eastWest.Enabled:
        return abort(404)

    form = DistributedStep1Form()
    if form.validate_on_submit():
        try:
            experimentName = request.form.get('name')
            exclusive = (len(request.form.getlist('exclusive')) != 0)
            testCases = request.form.getlist('Distributed_testCases')
            ues_selected = request.form.getlist('Distributed_ues')
            remotePlatform = request.form.get('remoteSelectorCheckboxedList')

            experiment = Experiment(
                name=experimentName, author=current_user,
                type="Distributed", exclusive=exclusive,
                test_cases=testCases, ues=ues_selected,
                automated=True, reservation_time=None,
                parameters={}, application=None,
                remotePlatform=remotePlatform, remoteDescriptor=None
            )

            if "enableSlicing" in request.form.keys():
                _addSliceInfo(request.form, experiment)

            db.session.add(experiment)
            db.session.commit()

            Log.I(f'Added experiment {experiment.id}')
            return redirect(url_for('experiment.configureRemote', experimentId=experiment.id))
        except Exception as e:
            flash(f'Exception creating distributed experiment (local): {e}', 'error')

    remotes = eastWest.RemoteNames
    nss: List[Tuple[str, int]] = []
    for ns in current_user.UsableNetworkServices:
         nss.append((ns.name, ns.id))

    return render_template('experiment/create_dist.html', title='New Distributed Experiment', form=form, nss=nss,
                           sliceList=Facility.BaseSlices(), scenarioList=Facility.Scenarios(), ues=Facility.UEs(),
                           ewEnabled=Config().EastWest.Enabled, remotes=['Here', 'There'],
                           distributedTestCases=Facility.DistributedTestCases())


@bp.route('/configure_remote/<experimentId>', methods=['GET', 'POST'])
@login_required
def configureRemote(experimentId: int):
    eastWest = Config().EastWest
    if not eastWest.Enabled:
        return abort(404)

    localExperiment = Experiment.query.get(experimentId)
    if localExperiment is None:
        flash(f'Experiment not found', 'error')
        return redirect(url_for('main.index'))

    if localExperiment.user_id is not current_user.id:
        flash(f'Forbidden - You don\'t have permission to access this experiment', 'error')
        return redirect(url_for('main.index'))

    form = DistributedStep2Form()
    if form.validate_on_submit():
        pass

    return render_template('experiment/configure_dist.html', title='New Distributed Experiment',
                           form=form, remote=localExperiment.remotePlatform)


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
                                       dispatcherUrl=config.ELCM.Url,  # TODO: Use dispatcher
                                       ewEnabled=Config().EastWest.Enabled)
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
