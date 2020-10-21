from typing import List, Dict, Set
from .log import Log


class Facility:
    ues: List[str] = []
    standard: List[str] = []
    custom: List[str] = []
    privateCustom: Dict[str, Set[str]] = {}
    distributed: List[str] = []
    parameters: Dict[str, List[Dict[str, str]]] = {}
    baseSlices: List[str] = []
    scenarios: List[str] = []

    @classmethod
    def Reload(cls):
        try:
            from REST import ElcmApi

            elcm = ElcmApi()
            Log.I('  Retrieving UEs...')
            ues = elcm.GetUEs()
            Log.I('  Retrieving TestCases...')
            testcases = elcm.GetTestCases()
            Log.I('  Retrieving Scenarios...')
            scenarios = elcm.GetScenarios()
            Log.I('  Retrieving Base Slice Descriptors (Slice Manager)...')
            baseSlices = elcm.GetBaseSlices()

            standard = []
            custom = []
            distributed = []
            privateCustom = {}
            parameters = {}

            for testcase in testcases:
                name = testcase['Name']
                parameters[name] = testcase['Parameters']
                if testcase['Standard']:
                    standard.append(name)
                if testcase['PublicCustom']:
                    custom.append(name)
                if testcase['Distributed']:
                    distributed.append(name)
                for email in sorted(testcase['PrivateCustom']):
                    if email not in privateCustom.keys():
                        privateCustom[email] = set()
                    privateCustom[email].add(name)

            Log.I(f'  {len(ues)} UEs, {len(scenarios)} Scenarios, {len(baseSlices)} Slice Descriptors')
            Log.I(f'  TestCases: {len(standard)} standard, {len(custom)} public custom, {len(distributed)} distributed')

            cls.ues = sorted(ues)
            cls.standard = sorted(standard)
            cls.custom = sorted(custom)
            cls.privateCustom = privateCustom
            cls.distributed = distributed
            cls.parameters = parameters
            cls.baseSlices = baseSlices
            cls.scenarios = scenarios
        except Exception as e:
            Log.E(f"Exception while reloading facility information: {e}")
            Log.W("Facility information not updated.")

    @classmethod
    def UEs(cls): return cls.ues

    @classmethod
    def StandardTestCases(cls): return cls.standard

    @classmethod
    def PublicCustomTestCases(cls): return cls.custom

    @classmethod
    def DistributedTestCases(cls): return cls.distributed

    @classmethod
    def BaseSlices(cls): return cls.baseSlices

    @classmethod
    def Scenarios(cls): return cls.scenarios

    @classmethod
    def PrivateCustomTestCases(cls, email: str):
        return cls.privateCustom.get(email, [])

    @classmethod
    def AvailableCustomTestCases(cls, email: str):
        return sorted([
            *cls.PublicCustomTestCases(),
            *cls.PrivateCustomTestCases(email)
        ])

    @classmethod
    def TestCaseParameters(cls): return cls.parameters
