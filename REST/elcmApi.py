import json
from typing import Dict
from app.models import Experiment
from .restClient import RestClient
from Helper import Config


class ElcmApi(RestClient):
    def __init__(self):
        config = Config().ELCM
        super().__init__(config.Host, config.Port, "")

    def Post(self, experimentId: int) -> Dict:
        url = f'{self.api_url}/api/v0/run'
        response = self.HttpPost(url, {'Content-Type': 'application/json'},
                                 json.dumps(Experiment.query.get(experimentId).serialization()))
        return RestClient.ResponseToJson(response)

    def GetLogs(self, executionId: int) -> Dict:
        url = f'{self.api_url}/execution/{executionId}/logs'
        response = self.HttpGet(url)
        return RestClient.ResponseToJson(response)
