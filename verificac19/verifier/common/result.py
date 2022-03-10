
class Result:
    def __init__(
        self,
        code: str,
        result: bool,
        message: str,
        name: str = "-",
        date_of_birth: str = "-",
    ):
        self._code = code
        self._result = result
        self._message = message
        self._name = name
        self._date_of_birth = date_of_birth

    def add_person(self, name: str, date_of_birth: str):
        self._name = name
        self._date_of_birth = date_of_birth
        return self

    @property
    def payload(self) -> dict:
        return {
            "code": self._code,
            "result": self._result,
            "message": self._message,
            "person": self._name,
            "date_of_birth": self._date_of_birth,
        }
