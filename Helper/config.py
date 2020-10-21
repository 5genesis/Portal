import yaml
import logging
from typing import Dict, List, Optional, Tuple, Union
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

    @property
    def Url(self):
        return f"{self.Host}:{self.Port}/"


class Dispatcher(hostPort):
    def __init__(self, data: Dict):
        super().__init__(data, 'Dispatcher')
        self.TokenExpiry = data['Dispatcher'].get('TokenExpiry', 240)


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


class EastWest:
    def __init__(self, data: Dict):
        self.data = data.get('EastWest', {})

    @property
    def Enabled(self) -> bool:
        return self.data.get('Enabled', False)

    @property
    def Remotes(self) -> Dict[str, Dict[str, Union[int, str]]]:
        return self.data.get('Remotes', {})

    @property
    def RemoteNames(self) -> List[str]:
        return list(self.Remotes.keys())

    def RemoteData(self, name: str) -> Optional[Tuple[str, int]]:
        try:
            remote = self.Remotes[name]
            return remote['Host'], remote['Port']
        except Exception:
            return None


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

            description = "No 'PlatformDescriptionPage' value set on config.yml"
            htmlFile = self.data.get("PlatformDescriptionPage", None)
            if htmlFile is not None:
                try:
                    with open(abspath(htmlFile), 'r', encoding="utf8") as stream:
                         description = stream.read()
                except Exception as e:
                    description = f"Exception while reading description html from {htmlFile}: {e}"
            self.data["PlatformDescriptionHtml"] = description

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
    def Platform(self):
        return self.data['Platform']

    @property
    def Description(self):
        return self.data['Description']

    @property
    def GrafanaUrl(self):
        return self.data['Grafana URL']

    @property
    def PlatformDescriptionHtml(self):
        return self.data.get("PlatformDescriptionHtml", self.Description)

    @property
    def Logging(self) -> Logging:
        return Logging(self.data)

    @property
    def EastWest(self) -> EastWest:
        return EastWest(self.data)