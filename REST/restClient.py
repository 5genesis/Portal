import re
import json
from typing import Dict
from urllib3 import connection_from_url
from os.path import realpath, join


class RestClient:
    HEADERS = {'Accept-Language': 'en-US;q=0.5,en;q=0.3'}
    RETRIES = 10
    FILENAME_PATTERN = re.compile(r".*filename=\"(.*)\"")

    def __init__(self, api_host, api_port, suffix):
        self.api_url = f'http://{api_host}:{api_port}{suffix}'
        self.pool = connection_from_url(self.api_url, maxsize=1, headers=self.HEADERS)

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
        return self.pool.request('GET',
                                 url,
                                 headers=extra_headers,
                                 retries=self.RETRIES)

    def HttpPost(self, url, extra_headers=None, body=''):
        extra_headers = {} if extra_headers is None else extra_headers
        return self.pool.request('POST',
                                 url,
                                 body=body,
                                 headers={**self.HEADERS, **extra_headers},
                                 retries=self.RETRIES)

    def HttpPatch(self, url, extra_headers=None, body=''):
        extra_headers = {} if extra_headers is None else extra_headers
        return self.pool.request('PATCH',
                                 url,
                                 body=body,
                                 headers={**self.HEADERS, **extra_headers},
                                 retries=self.RETRIES)

    @staticmethod
    def ResponseToJson(response) -> Dict:
        return json.loads(response.data.decode('utf-8'))
