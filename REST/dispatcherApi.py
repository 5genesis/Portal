import json
from typing import Dict, Tuple, Optional, List
from app.models import User, Experiment
from .restClient import RestClient, Payload
from base64 import b64encode
from Helper import Config, Log, LogInfo
from app import db
from datetime import datetime, timezone
from os.path import split


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

    def Register(self, user: User) -> Tuple[str, bool]:
        """ Returns (<message>, <success>). """
        url = '/auth/register'
        data = {
            'username': user.username,
            'email': user.email,
            'password': user.password_hash
        }
        try:
            response = self.HttpPost(url, body=data, payload=Payload.Form)
            status = self.ResponseStatusCode(response)
            if status in [400, 200]:
                message = self.ResponseToJson(response)['result']
                return message, (status == 200)
            else:
                raise Exception(f"Status {status} ({response.reason})")
        except Exception as e:
            return f"Exception while accessing authentication: {e}", False

    def GetToken(self, user: User) -> Tuple[str, bool]:
        """
        Return a tuple (str, bool). The string contains the token OR the
        error message, the boolean indicates success.
        """
        url = '/auth/get_token'
        try:
            response = self.HttpGet(url, extra_headers=self.basicAuthHeader(user.username, user.password_hash))
            status = self.ResponseStatusCode(response)
            if status in [400, 200]:
                result = self.ResponseToJson(response)['result']
                return result, (status == 200)
            else:
                raise Exception(f"Status {status} ({response.reason})")
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
        url = f'/elcm/api/v0/run'
        response = self.HttpPost(url, {'Content-Type': 'application/json', **self.bearerAuthHeader(token)}, descriptor)
        status = RestClient.ResponseStatusCode(response)
        if status != 200:
            return {"ExecutionId": None, "Success": False,
                    "Message": f"Execution request failed with status {status}"}
        else:
            response = RestClient.ResponseToJson(response)
            response.update({"Success": True, "Message": "No error"})
            return response

    def GetExecutionLogs(self, executionId: int, user: User) -> Dict:
        maybeError = self.RenewUserTokenIfExpired(user)
        if maybeError is not None:
            empty = LogInfo.Empty()
            return {'PreRun': empty, 'Executor': empty, 'PostRun': empty, 'Status': maybeError}

        token = user.CurrentDispatcherToken
        url = f'/elcmexecution/{executionId}/logs'
        response = self.HttpGet(url, extra_headers=self.bearerAuthHeader(token))
        return RestClient.ResponseToJson(response)

    def basicGet(self, user: User, url: str, action: str) -> Tuple[object, Optional[str]]:
        try:
            maybeError = self.RenewUserTokenIfExpired(user)
            if maybeError is not None:
                return {}, maybeError

            token = user.CurrentDispatcherToken
            response = self.HttpGet(url, extra_headers=self.bearerAuthHeader(token))
            return self.ResponseToJson(response), None
        except Exception as e:
            return {}, f"Exception while {action}: {e}"

    def GetVimLocations(self, user: User) -> Tuple[List[VimInfo], Optional[str]]:
        data, error = self.basicGet(user, '/mano/vims', 'retrieving list of VIMs')  # type: List, Optional[str]
        return [VimInfo(vim) for vim in data] if error is None else [], error

    def GetVimLocationImages(self, user: User, location: str) -> Tuple[List[VimInfo], Optional[str]]:
        data, error = self.basicGet(user, '/mano/image', f"list of images for VIM '{location}'")  # type: Dict, Optional[str]
        return data.get(location, []) if error is None else [], error

    def GetAvailableVnfds(self, user: User) -> Tuple[List[str], Optional[str]]:
        data, error = self.basicGet(user, '/mano/vnfd', f"list of VNFDs")  # type: Dict, Optional[str]
        return data if error is None else [], error

    def GetAvailableNsds(self, user: User) -> Tuple[List[str], Optional[str]]:
        data, error = self.basicGet(user, '/mano/nsd', f"list of NSDs")  # type: Dict, Optional[str]
        return data if error is None else [], error

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

    def OnboardVnfd(self, path: str, token: str, visibility: bool) -> Tuple[str, bool]:
        """Returns a pair of str (id or error message) and bool (success)"""

        url = '/mano/vnfd'
        overrides = {409: "Conflict - VNFD already present"}
        return self._onboardVnfdOrNsd(url, path, token, 'VNFs', overrides, visibility)

    def OnboardNsd(self, path: str, token: str, visibility: bool) -> Tuple[str, bool]:
        """Returns a pair of str (id or error message) and bool (success)"""

        url = '/mano/nsd'
        overrides = {409: "Conflict - NSD already present"}
        return self._onboardVnfdOrNsd(url, path, token, "NSs", overrides, visibility)

    def _onboardVnfdOrNsd(self, url: str, path: str, token: str, dictId: str, overrides: Dict, visibility: bool):
        with open(path, "br") as file:
            data = {'visibility': str(visibility).lower()}
            response = self.HttpPost(url, extra_headers=self.bearerAuthHeader(token), files={'file': file},
                                     body=data, payload=Payload.Form)

            code = self.ResponseStatusCode(response)
            data = self.ResponseToJson(response)
            if code == 200:
                try:
                    return list(data[dictId].keys())[0], True
                except (KeyError, IndexError, AttributeError):
                    return split(path)[1], True
            elif code == 400:
                try:
                    return data['error'], False
                except KeyError:
                    return str(data), False
            else:
                return self.handleErrorcodes(code, data, overrides), False

    def OnboardVim(self, path: str, location: str, token: str, visibility: str) -> Optional[str]:
        """Returns an error message, or None on success"""

        with open(path, "br") as file:
            containerFormat = "bare"
            data = {'vim_id': location, 'container_format': containerFormat,
                    'visibility': str(visibility).lower()}
            response = self.HttpPost('/mano/image', extra_headers=self.bearerAuthHeader(token),
                                     body=data, files={'file': file}, payload=Payload.Form)
            code = self.ResponseStatusCode(response)

        if code == 200:
            return None
        else:
            try:
                data = self.ResponseToJson(response)
                return data.get('detail', data.get('result', f'Unknown error. Status code: {code}'))
            except Exception as e:
                raise Exception(f"Unknown exception '{e}'. Status code: {code}")
