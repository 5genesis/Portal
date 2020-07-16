import json
from typing import Dict, List, Optional
from app.models import Experiment
from .restClient import RestClient
from Helper import Config


class ElcmApi(RestClient):
    def __init__(self):
        config = Config().ELCM
        super().__init__(config.Host, config.Port, "")

    def Run(self, experimentId: int) -> Dict:
        url = f'{self.api_url}/api/v0/run'
        response = self.HttpPost(url, {'Content-Type': 'application/json'},
                                 json.dumps(Experiment.query.get(experimentId).serialization()))
        return RestClient.ResponseToJson(response)

    def GetLogs(self, executionId: int) -> Dict:
        url = f'{self.api_url}/execution/{executionId}/logs'
        response = self.HttpGet(url)
        return RestClient.ResponseToJson(response)

    def GetUEs(self) -> Optional[List[str]]:
        url = f'{self.api_url}/facility/ues'
        try:
            response = self.HttpGet(url)
            return self.ResponseToJson(response)['UEs']
        except Exception:
            return None

    def GetTestCases(self) -> Optional[List[Dict[str, object]]]:
        url = f'{self.api_url}/facility/testcases'
        try:
            response = self.HttpGet(url)
            return self.ResponseToJson(response)['TestCases']
        except Exception:
            return None

    def GetBaseSlices(self) -> List[str]:
        url = f'{self.api_url}/facility/baseSliceDescriptors'
        try:
            response = self.HttpGet(url)
            return self.ResponseToJson(response)
        except Exception:
            return []
