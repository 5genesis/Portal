from .child import Child
from typing import Dict, Optional
from config import Config
from os.path import join, abspath, exists
from os import remove


class Action(Child):
    def __init__(self, service, type: str, vnfd, token):
        super().__init__(f"{service.id}_{type}")
        self.service = service  # type: "NetworkService"
        self.type = type
        self.vnfd = vnfd  # type: "VnfdPackage"
        self.token = token
        self.message = "Init"
        self.result = None

    def Run(self):
        try:
            handler = getattr(self, self.type)
            handler()
        except Exception as e:
            self.hasFailed = True
            self.message = f"Error: {e}"

    def onboardVim(self):
        from REST import DispatcherApi

        filePath = abspath(join(Config.UPLOAD_FOLDER, *self.service.VimLocalPath, self.service.vim_image))
        vimName = self.service.vim_name
        self.message = f"VIM Image onboarding in progress"
        maybeError = DispatcherApi().OnboardVim(filePath, vimName, self.token, self.service.is_public)

        if maybeError is None:
            self.result = "<onboarded>"  # Not a known ID but a value to signal it's been onboarded
            self.message = f"VIM Image successfully onboarded"
        else:
            raise RuntimeError(f"Exception during onboarding process: {maybeError}")

    def onboardNsd(self):
        from REST import DispatcherApi

        filePath = abspath(join(Config.UPLOAD_FOLDER, *self.service.NsdLocalPath, self.service.nsd_file))
        self.message = f"NSD file onboarding in progress"
        maybeId, success = DispatcherApi().OnboardNsd(filePath, self.token, self.service.is_public)

        if success:
            self.result = maybeId
            self.message = f"NSD file successfully onboarded"
        else:
            raise RuntimeError(f"Exception during onboarding process: {maybeId}")

    def onboardVnf(self):
        from REST import DispatcherApi

        filePath = abspath(join(Config.UPLOAD_FOLDER, *self.vnfd.VnfdLocalPath, self.vnfd.vnfd_file))
        self.message = f"VNFD package onboarding in progress"
        maybeId, success = DispatcherApi().OnboardVnfd(filePath, self.token, self.service.is_public)

        if success:
            self.result = maybeId
            self.message = f"Onboarded VNFD with id: {maybeId}"
        else:
            raise RuntimeError(f"Exception during onboarding process: {maybeId}")

    def deleteVim(self):
        if self.service.vim_id is not None:
            self.message = "Deletion of onboarded VIM images is not supported"
        else:
            self.message = "Deleting VIM image"
            self._deleteLocalFile(self.service.VimLocalPath, self.service.vim_image)
            self.message = "Deleted VIM image from temporal storage"

    def deleteNsd(self):
        if self.service.nsd_id is not None:
            self.message = "Deletion of onboarded NSD is not supported"
        else:
            self.message = "Deleting NSD file"
            self._deleteLocalFile(self.service.NsdLocalPath, self.service.nsd_file)
            self.message = "Deleted NSD file from temporal storage"

    def deleteVnf(self):
        if self.vnfd.vnfd_id is not None:
            self.message = "Deletion of onboarded VNFDs is not supported"
        else:
            self.message = "Deleting VNFD package"
            self._deleteLocalFile(self.vnfd.VnfdLocalPath, self.vnfd.vnfd_file)
            self.message = "Deleted VNFD package file from temporal storage"

    def _deleteLocalFile(self, path, file):
        filePath = abspath(join(Config.UPLOAD_FOLDER, *path, file))
        if exists(filePath):
            remove(filePath)

    def __str__(self):
        return f"Action: {self.name} (St:{self.hasStarted}, Ed:{self.hasFinished}, Fail:{self.hasFailed})"


class ActionHandler:
    collection: Dict[int, Action] = {}

    @classmethod
    def Get(cls, id: int) -> Optional[Action]:
        return cls.collection.get(id, None)

    @classmethod
    def Set(cls, id: int, action: Action) -> None:
        if id in cls.collection.keys():
            from .log import Log
            Log.W(f"Adding duplicated key to active Actions ({id}), overwritting existing: {cls.collection[id]}")
        cls.collection[id] = action

    @classmethod
    def Delete(cls, id: int) -> None:
        _ = cls.collection.pop(id)


