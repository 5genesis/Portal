import re
import json
from typing import Dict, Union, Optional
from urllib3 import connection_from_url
from requests import post
from os.path import realpath, join
from enum import Enum, unique


@unique
class Payload(Enum):
    Form = 0
    Data = 1


class RestClient:
    HEADERS = {'Accept-Language': 'en-US;q=0.5,en;q=0.3'}
    RETRIES = 10
    FILENAME_PATTERN = re.compile(r".*filename=\"(.*)\"")

    def __init__(self, api_host, api_port, suffix, https=False, insecure=False):
        self.api_url = f'http{"s" if https else ""}://{api_host}:{api_port}{suffix}'

        kw = {'maxsize': 1, 'headers': self.HEADERS}
        if https and insecure:
           kw['cert_reqs'] = 'CERT_NONE'

        self.pool = connection_from_url(self.api_url, **kw)
        self.insecure = insecure

    def Trace(self, url, method, headers=None, body=None, files=None):
        from Helper import Log
        Log.D(f"[{method}] {self.api_url}/{url}")
        for name, param in [('Headers', headers), ('Body', body), ('Files', files)]:
            if param is not None:
                Log.D(f'{name}: {param}')

    def DownloadFile(self, url, output_folder):
        response = self.HttpGet(url)
        filename = self.GetFilename(response.headers["Content-Disposition"])
        output_file = realpath(join(output_folder, filename))

        with open(output_file, 'wb+') as out:
            out.write(response.data)

        response.release_conn()
        return output_file

    def GetFilename(self, content_disposition):
        result = self.FILENAME_PATTERN.match(content_disposition)
        if result is not None:
            return result.group(1)
        return "unknown_filename"

    def HttpGet(self, url, extra_headers=None):
        extra_headers = {} if extra_headers is None else extra_headers
        self.Trace(url, 'GET', headers=extra_headers)
        return self.pool.request('GET',
                                 url,
                                 headers=extra_headers,
                                 retries=self.RETRIES)

    def HttpPost(self, url, extra_headers=None, body: Optional[Union[str, Dict]] = None,
                 files=None, payload: Payload = None):
        extra_headers = {} if extra_headers is None else extra_headers

        if payload == Payload.Data:
            extra_headers['Content-Type'] = 'application/json'
            if isinstance(body, Dict):
                body = json.dumps(body)
        elif payload == Payload.Form:
            if files is None:
                extra_headers['Content-Type'] = 'application/x-www-form-urlencoded'
                if isinstance(body, str):
                    body = self.JsonToUrlEncoded(body)
                elif isinstance(body, Dict):
                    body = self.DictToUrlEncoded(body)
            else:  # Do not add any Content-Type, and ensure that body is a Dict
                if not isinstance(body, Dict):
                    raise ValueError("For POST requests with files the body must be a Dict")

        self.Trace(url, 'POST', headers=extra_headers, body=body, files=files)

        if files is None:
            return self.pool.request('POST', url, body=body or '', headers={**self.HEADERS, **extra_headers},
                                     retries=self.RETRIES)
        else:
            return post(f"{self.api_url}{url}", data=body, headers={**self.HEADERS, **extra_headers},
                        files=files, verify=not self.insecure)

    def HttpPatch(self, url, extra_headers=None, body=''):
        extra_headers = {} if extra_headers is None else extra_headers
        self.Trace(url, 'PATCH', headers=extra_headers, body=body)
        return self.pool.request('PATCH',
                                 url,
                                 body=body,
                                 headers={**self.HEADERS, **extra_headers},
                                 retries=self.RETRIES)

    def HttpDelete(self, url, extra_headers=None):
        extra_headers = {} if extra_headers is None else extra_headers
        self.Trace(url, 'DELETE', headers=extra_headers)
        return self.pool.request('DELETE', url, headers={**self.HEADERS, **extra_headers}, retries=self.RETRIES)

    @staticmethod
    def ResponseStatusCode(response) -> int:
        try:
            return response.status
        except AttributeError:
            return response.status_code

    @staticmethod
    def ResponseToJson(response) -> object:
        try:
            raw = response.data if hasattr(response, 'data') else response.content
        except Exception as e:
            raise RuntimeError(f"Could not extract raw data from response: {e}")

        try:
            return json.loads(raw.decode('utf-8'))
        except Exception as e:
            raise RuntimeError(f'JSON parse exception: {e}. data={response.data}')

    @staticmethod
    def JsonToUrlEncoded(jsonData: str) -> str:
        try:
            return RestClient.DictToUrlEncoded(json.loads(jsonData))
        except Exception as e:
            raise RuntimeError(f'JSON parse exception: {e}. data={jsonData}')

    @staticmethod
    def DictToUrlEncoded(dict: Dict) -> str:
        return "&".join(f"{key}={value}" for key, value in dict.items())
