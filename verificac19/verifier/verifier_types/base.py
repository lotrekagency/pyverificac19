from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError

class BaseVerifier:

    def __init__(self, dcc: dcc.DCC):
        self.dcc = dcc

    def result(self):
        raise NotImplementedError
