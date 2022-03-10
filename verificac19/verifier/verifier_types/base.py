from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError

class BaseVerifier:

    def __init__(self, dcc: dcc.DCC):
        self.dcc = dcc
        self.payload = self.dcc.payload

    def calculate_result(self):
        raise NotImplementedError
