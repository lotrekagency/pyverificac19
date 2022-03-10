from verificac19.verifier.common.result import Result

class VerificaC19Error(Exception):
    pass

class VerificationComplete(Exception):

    def __init__(self, result:Result, *args, **kwargs) -> None:
        self.result = result
        super().__init__(*args, **kwargs)

class VerificationNoResult(Exception):
    pass
