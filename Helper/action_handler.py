from .child import Child
from typing import Dict, Optional
from time import sleep
from .log import Level


class Action(Child):
    def __init__(self, service, type: str, vnfd):
        self.service = service  # type: "NetworkService"
        self.vnfd = vnfd  # type: "VnfdPackage"
        self.type = type
        super().__init__(f"{self.service.id}_{self.type}")
        self.message = "Init"
        self.result = None

    def Run(self):
        for i in range(10):
            self.Log(Level.INFO, f"{self.name} -> {i}")
            self.message = str(i)
            sleep(1)
        self.result = "placeholder"

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


