from app.east_west import bp
from flask import jsonify
from Helper import Facility
from app.models import NetworkService
from REST import ElcmApi


@bp.route('/testcases', methods=['GET'])
def testcases():
    return jsonify({'TestCases': Facility.DistributedTestCases()})


@bp.route('/ues', methods=['GET'])
def ues():
    return jsonify({'UEs': Facility.UEs()})


@bp.route('/baseSliceDescriptors', methods=['GET'])
def baseSliceDescriptors():
    return jsonify({'SliceDescriptors': Facility.BaseSlices()})


@bp.route('/scenarios', methods=['GET'])
def scenarios():
    return jsonify({'Scenarios': Facility.Scenarios()})


@bp.route('/networkServices', methods=['GET'])
def networkServices():
    return jsonify({
        'NetworkServices': [(ns.name, ns.nsd_id, ns.vim_location) for ns in NetworkService.PublicServices() if ns.Ready]
    })


@bp.route('/executionLogs/<executionId>', methods=['GET'])
def executionLogs(executionId: int):
    return ElcmApi().GetLogs(executionId)
