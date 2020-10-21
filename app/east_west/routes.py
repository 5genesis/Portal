from app.east_west import bp
from flask import jsonify
from Helper import Facility


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
