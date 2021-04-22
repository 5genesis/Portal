import jwt
from typing import List, Tuple


class Crypt:
    def __init__(self, secret: str):
        self.secret = secret

    def Encode(self, target: int, executions: List[int]) -> str:
        """'target' is the landing experiment execution, 'executions' is
        the list of all executions belonging to the user"""
        payload = {"t": target, "l": executions}
        token = jwt.encode(payload, self.secret, algorithm="HS256")
        if isinstance(token, bytes):  # Older versions of jwt return bytes
            token = token.decode(encoding="UTF-8")
        return token

    def Decode(self, token: str) -> Tuple[int, List[int]]:
        """Returns a tuple (<landing execution>, <list of executions>)"""
        payload = jwt.decode(token, self.secret, algorithms=["HS256"])
        return payload["t"], payload["l"]
