from typing import List
from .restClient import RestClient


class RemoteApi(RestClient):
    def __init__(self, host, port):
        super().__init__(host, port, "/distributed")

    def getData(self, url, key) -> List[str]:
        try:
            response = self.HttpGet(url)
            return RestClient.ResponseToJson(response)[key]
        except Exception:
            return []

    def GetTestCases(self) -> List[str]:
        return self.getData(f'{self.api_url}/testcases', "TestCases")

    def GetUEs(self) -> List[str]:
        return self.getData(f'{self.api_url}/ues', "UEs")

    def GetBaseSlices(self) -> List[str]:
        return self.getData(f'{self.api_url}/baseSliceDescriptors', 'SliceDescriptors')

    def GetScenarios(self) -> List[str]:
        return self.getData(f'{self.api_url}/scenarios', 'Scenarios')
