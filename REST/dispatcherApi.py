import json
from typing import Dict, Tuple, Optional, List
from app.models import User, Experiment
from .restClient import RestClient
from base64 import b64encode
from Helper import Config, Log, LogInfo
from app import db
from datetime import datetime, timezone


class VimInfo:
    def __init__(self, data):
        self.Name = data['name']
        self.Type = data['type']
        self.Location = data['location']

    def __str__(self):
        return f'{self.Name} ({self.Type} - {self.Location})'


class DispatcherApi(RestClient):
    def __init__(self):
        config = Config().Dispatcher
        super().__init__(config.Host, config.Port, "", https=True, insecure=True)
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
        user.tokenTimestamp = datetime.now(timezone.utc) if success else None
        db.session.add(user)
        db.session.commit()
        return token if not success else None

    def RenewUserTokenIfExpired(self, user) -> Optional[str]:
        """Returns None if no error, an error message otherwise"""
        tokenTimestamp = user.tokenTimestamp if user.tokenTimestamp is not None else datetime.min
        tokenTimestamp = tokenTimestamp.replace(tzinfo=timezone.utc)
        timespan = datetime.now(timezone.utc) - tokenTimestamp
        if timespan.total_seconds() >= self.tokenExpiry:
            return self.RenewUserToken(user)
        else:
            return None

    def RunCampaign(self, experimentId: int, user: User) -> Dict:
        maybeError = self.RenewUserTokenIfExpired(user)
        if maybeError is not None:
            return {"ExecutionId": None, "Success": False, "Message": maybeError}

        token = user.CurrentDispatcherToken
        descriptor = json.dumps(Experiment.query.get(experimentId).serialization())
        url = f'/elcmapi/v0/run'  # TODO: See if this can be improved
        response = self.HttpPost(url, {'Content-Type': 'application/json', **self.bearerAuthHeader(token)}, descriptor)
        return RestClient.ResponseToJson(response)

    def GetExecutionLogs(self, executionId: int, user: User) -> Dict:
        maybeError = self.RenewUserTokenIfExpired(user)
        if maybeError is not None:
            empty = LogInfo.Empty()
            return {'PreRun': empty, 'Executor': empty, 'PostRun': empty, 'Status': maybeError}

        token = user.CurrentDispatcherToken
        url = f'/elcmexecution/{executionId}/logs'
        response = self.HttpGet(url, extra_headers=self.bearerAuthHeader(token))
        return RestClient.ResponseToJson(response)

    def GetVimLocations(self, user: User) -> Tuple[List[VimInfo], Optional[str]]:
        result = []
        maybeError = self.RenewUserTokenIfExpired(user)
        if maybeError is not None:
            return result, maybeError

        token = user.CurrentDispatcherToken
        url = '/mano/vims'
        response = self.HttpGet(url, extra_headers=self.bearerAuthHeader(token))
        result = [VimInfo(vim) for vim in self.ResponseToJson(response)]

        return result, None

    def handleErrorcodes(self, code: int, data: Dict, overrides: Dict[int, str] = None) -> str:
        defaults = {
            400: "Invalid Input",
            401: "Invalid permission",
            404: "Not found",
            406: "File not valid",
            409: "Conflict",
            413: "File too large",
            422: "Unprocessable entity",
            500: "Internal server error"  # Or an unknown error code
        }
        overrides = {} if overrides is None else overrides
        error = overrides.get(code, defaults.get(code, defaults[500]))
        if code in [400, 404, 409, 422]:
            extra = f" (Status: {data['status']}, Code: {data['code']}, Detail: {data['detail']})"
        elif code == 401:
            extra = ""
        else:
            extra = f" (Code {code})"
        return error + extra

    def OnboardVnfd(self, path: str, token: str) -> Tuple[str, bool]:
        """Returns a pair of str (id or error message) and bool (success)"""

        url = '/mano/vnfd'
        with open(path, "br") as file:
            response = self.HttpPost(url, extra_headers=self.bearerAuthHeader(token), files={'vnfd': file})
            code = self.ResponseStatusCode(response)
            data = self.ResponseToJson(response)
            if code == 200:
                return data["id"], True
            else:
                overrides = {409: "Conflict - VNFD already present"}
                return self.handleErrorcodes(code, data, overrides), False

    def DeleteVnfd(self, vnfdId: str, token: str) -> Optional[str]:
        """Returns an error message, or None on success"""

        url = f'/mano/vnfd/{vnfdId}'
        response = self.HttpDelete(url, extra_headers=self.bearerAuthHeader(token))
        code = self.ResponseStatusCode(response)
        if code != 204:
            data = self.ResponseToJson(response)
            overrides = {404: "VNFD not found", 409: "Conflict - VNFD referenced by at least one NSD"}
            return self.handleErrorcodes(code, data, overrides)
        else:
            return None
