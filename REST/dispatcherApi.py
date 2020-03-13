import json
from typing import Dict, Tuple, Optional
from app.models import User, Experiment
from .restClient import RestClient
from base64 import b64encode
from Helper import Config, Log, LogInfo
from app import db
from datetime import datetime


class DispatcherApi(RestClient):
    def __init__(self):
        config = Config().Dispatcher
        super().__init__(config.Host, config.Port, "")
        self.tokenExpiry = config.TokenExpiry

    @staticmethod
    def basicAuthHeader(user: str, password: str) -> Dict:
        encoded = b64encode(bytes(f'{user}:{password}'.encode('ascii')))
        return {'Authorization': f'Basic {encoded.decode("ascii")}'}

    @staticmethod
    def bearerAuthHeader(token: str) -> Dict:
        return {'Authorization': f'Bearer {token}'}

    def Register(self, user: User) -> Dict:
        url = '/auth/register'
        data = {
            'username': user.username,
            'email': user.email,
            'password': user.password_hash
        }
        response = self.HttpPost(url, {'Content-Type': 'application/json'}, json.dumps(data))
        return self.ResponseToJson(response)

    def GetToken(self, user: User) -> Tuple[str, bool]:
        """
        Return a tuple (str, bool). The string contains the token OR the
        error message, the boolean indicates success.
        """
        url = '/auth/get_token'
        try:
            response = self.HttpGet(url, extra_headers=self.basicAuthHeader(user.username, user.password_hash))
            if response.status is not 200:
                raise Exception(f"Status {response.status} ({response.reason})")
            maybeToken = self.ResponseToJson(response)['result']
            if "No user" in maybeToken or "not activated" in maybeToken:
                raise Exception(maybeToken)
            return maybeToken, True
        except Exception as e:
            message = f"Error while retrieving token: {e}"
            Log.E(message)
            return message, False

    def RenewUserToken(self, user: User) -> Optional[str]:
        """Returns None if no error, an error message otherwise"""
        token, success = self.GetToken(user)
        user.token = token if success else None
        user.tokenTimestamp = datetime.utcnow() if success else None
        db.session.add(user)
        db.session.commit()
        return token if not success else None

    def RenewUserTokenIfExpired(self, user) -> Optional[str]:
        """Returns None if no error, an error message otherwise"""
        tokenTimestamp = user.tokenTimestamp if user.tokenTimestamp is not None else datetime.min
        timespan = datetime.utcnow() - tokenTimestamp
        if timespan.total_seconds() >= self.tokenExpiry:
            return self.RenewUserToken(user)
        else:
            return None

    def RunCampaign(self, experimentId: int, user: User) -> Dict:
        maybeError = self.RenewUserTokenIfExpired(user)
        if maybeError is not None:
            return {"ExecutionId": None, "Success": False, "Message": maybeError}

        token = user.getCurrentDispatcherToken()
        descriptor = json.dumps(Experiment.query.get(experimentId).serialization())
        url = f'/elcmapi/v0/run'  # TODO: See if this can be improved
        response = self.HttpPost(url, {'Content-Type': 'application/json', **self.bearerAuthHeader(token)}, descriptor)
        return RestClient.ResponseToJson(response)

    def GetExecutionLogs(self, executionId: int, user: User) -> Dict:
        maybeError = self.RenewUserTokenIfExpired(user)
        if maybeError is not None:
            empty = LogInfo.Empty()
            return {'PreRun': empty, 'Executor': empty, 'PostRun': empty, 'Status': maybeError}

        token = user.getCurrentDispatcherToken()
        url = f'/elcmexecution/{executionId}/logs'
        response = self.HttpGet(url, extra_headers=self.bearerAuthHeader(token))
        return RestClient.ResponseToJson(response)

