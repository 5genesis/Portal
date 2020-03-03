import json
from typing import Dict, Tuple
from app.models import User
from .restClient import RestClient
from base64 import b64encode
from Helper import Config, Log
from app import db


class DispatcherApi(RestClient):
    def __init__(self):
        config = Config().Dispatcher
        super().__init__(config.Host, config.Port, "")

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

    def RenewUserToken(self, user: User):
        token, success = self.GetToken(user)
        user.token = token if success else None
        db.session.add(user)
        db.session.commit()

    def RunCampaign(self, experimentId: int, user_id: int) -> Dict:
        user = User.query.get(user_id)
        token = user.getCurrentDispatcherToken()
        return {}

