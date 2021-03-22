from Helper import Crypt, Config
from app.models import User, Experiment
from typing import List


class AnalyticsApi:
    crypt = None
    url = None

    def __init__(self):
        if AnalyticsApi.crypt is None:
            config = Config().Analytics
            if config.Enabled:
                AnalyticsApi.url = config.Url
                AnalyticsApi.crypt = Crypt(config.Secret) if config.Secret is not None else None

    def GetToken(self, target: int, user: User) -> str:
        if self.crypt is not None:
            experiments: List[Experiment] = list(user.Experiments)
            executions = []
            for experiment in experiments:
                executions.extend(experiment.experimentExecutions())

            # TODO: Consider filtering the list with `execution.status == "Finished"`
            executions = sorted([execution.id for execution in executions])
            return self.crypt.Encode(target, executions)
        else:
            return "<Analytics disabled or no Secret>"

    def GetUrl(self, target: int, user: User) -> str:
        return f"{self.url}/endpoint?token={self.GetToken(target, user)}"
