import json
from typing import Dict
from app.models import User
from .restClient import RestClient


class AuthApi(RestClient):

    def __init__(self, api_host, api_port, suffix):
        super().__init__(api_host, api_port, suffix)

    def Register(self, user: User):
        url = f'/register'
        data = {
            'username': user.username,
            'email': user.email,
            'password': user.password_hash
        }
        response = self.HttpPost(url, {'Content-Type': 'application/json'}, json.dumps(data))
        return self.ResponseToJson(response)
