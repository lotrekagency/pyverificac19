from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError
from verificac19.exceptions import VerificationComplete, VerificationNoResult

class BaseVerifier:


    def __init__(self, dcc: dcc.DCC):
        self.dcc = dcc
        self.payload = self.dcc.payload

    def verify(self):
        try:
            self.start_verification()
        except VerificationComplete as e:
            self.result = e.result
            return e.result

        raise VerificationNoResult

    def start_verification(self):
        raise NotImplementedError
