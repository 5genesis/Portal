from .child import Child
from typing import Dict, Optional
from time import sleep
from .log import Level


class Action(Child):
    def __init__(self, serviceId: int , type: str):
        super().__init__(f"{serviceId}_{type}")
        self.serviceId = serviceId
        self.type = type
        self.message = "Init"

    def Run(self):
        for i in range(10):
            self.Log(Level.INFO, f"{self.name} -> {i}")
            self.message = str(i)
            sleep(2)
        pass

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


