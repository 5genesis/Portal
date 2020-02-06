import yaml
import logging
from typing import Dict, List
from shutil import copy
from os.path import exists, abspath


class hostPort:
    def __init__(self, data: Dict, key: str):
        self.data = data[key]

    @property
    def Host(self):
        return self.data['Host']

    @property
    def Port(self):
        return self.data['Port']


class Dispatcher(hostPort):
    def __init__(self, data: Dict):
        super().__init__(data, 'Dispatcher')


class ELCM(hostPort):
    def __init__(self, data: Dict):
        super().__init__(data, 'ELCM')


class Logging:
    def __init__(self, data: Dict):
        self.data = data['Logging']

    @staticmethod
    def toLogLevel(level: str) -> int:
        if level.lower() == 'critical': return logging.CRITICAL
        if level.lower() == 'error': return logging.ERROR
        if level.lower() == 'warning': return logging.WARNING
        if level.lower() == 'info': return logging.INFO
        return logging.DEBUG

    @property
    def Folder(self):
        return abspath(self.data['Folder'])

    @property
    def AppLevel(self):
        return self.toLogLevel(self.data['AppLevel'])

    @property
    def LogLevel(self):
        return self.toLogLevel(self.data['LogLevel'])


class Config:
    FILENAME = 'config.yml'
    FILENAME_NOTICES = 'notices.yml'
    data = None

    def __init__(self):
        if self.data is None:
            self.Reload()

    def Reload(self):
        if not exists(self.FILENAME):
            copy('Helper/defaultConfig', self.FILENAME)

        with open(self.FILENAME, 'r', encoding='utf-8') as file:
            self.data = yaml.safe_load(file)

    @property
    def Notices(self) -> List[str]:
        if not exists(self.FILENAME_NOTICES):
            return []

        with open(self.FILENAME_NOTICES, 'r', encoding='utf-8') as file:
            notices = yaml.safe_load(file)
            return notices['Notices']

    @property
    def Dispatcher(self) -> Dispatcher:
        return Dispatcher(self.data)

    @property
    def ELCM(self) -> Dispatcher:
        return ELCM(self.data)

    @property
    def TestCases(self):
        return self.data['TestCases']

    @property
    def UEs(self):
        return self.data['UEs']

    @property
    def Platform(self):
        return self.data['Platform']

    @property
    def Description(self):
        return self.data['Description']

    @property
    def Slices(self):
        return self.data['Slices']

    @property
    def GrafanaUrl(self):
        return self.data['Grafana URL']

    @property
    def Logging(self) -> Logging:
        return Logging(self.data)
