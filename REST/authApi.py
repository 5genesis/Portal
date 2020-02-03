import json
from typing import Dict
from app.models import User
from .restClient import RestClient
from base64 import b64encode


class AuthApi(RestClient):

    def __init__(self, api_host, api_port, suffix):
        super().__init__(api_host, api_port, suffix)

    def Register(self, user: User):
        url = '/register'
        data = {
            'username': user.username,
            'email': user.email,
            'password': user.password_hash
        }
        response = self.HttpPost(url, {'Content-Type': 'application/json'}, json.dumps(data))
        return self.ResponseToJson(response)

    def GetToken(self, user: User):
        url = '/get_token'
        encoded = b64encode(bytes(f'{user.username}:{user.password_hash}'.encode('ascii')))
        response = self.HttpGet(url, extra_headers={'Authorization': f'Basic {encoded.decode("ascii")}'})
        return self.ResponseToJson(response)
