from typing import List, Dict, Set
from .log import Log


class Facility:
    ues: List[str] = []
    standard: List[str] = []
    custom: List[str] = []
    privateCustom: Dict[str, Set[str]] = {}

    @classmethod
    def Reload(cls):
        try:
            from REST import ElcmApi

            elcm = ElcmApi()
            ues = elcm.GetUEs()
            testcases = elcm.GetTestCases()

            standard = []
            custom = []
            privateCustom = {}

            for testcase in testcases:
                name = testcase['Name']
                if testcase['Standard']:
                    standard.append(name)
                if testcase['PublicCustom']:
                    custom.append(name)
                for email in sorted(testcase['PrivateCustom']):
                    if email not in privateCustom.keys():
                        privateCustom[email] = set()
                    privateCustom[email].add(name)

            cls.ues = sorted(ues)
            cls.standard = sorted(standard)
            cls.custom = sorted(custom)
            cls.privateCustom = privateCustom
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
    def PrivateCustomTestCases(cls, email: str):
        return cls.privateCustom.get(email, [])

    @classmethod
    def AvailableCustomTestCases(cls, email: str):
        return sorted([
            *cls.PublicCustomTestCases(),
            *cls.PrivateCustomTestCases(email)
        ])
