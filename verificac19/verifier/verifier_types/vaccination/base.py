from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError
from verificac19.verifier.verifier_types.base import BaseVerifier
from verificac19.verifier.common.result import Result

class BaseVaccination(BaseVerifier):

    def __init__(self, dcc: dcc.DCC, *args, **kwargs):
        super().__init__(dcc, *args, **kwargs)

    def base_verification(self):
        if len(self.payload["v"]) == 0:
            return Result(
                self.Codes.NOT_EU_DCC,
                False,
                "No vaccination, test, recovery or exemption statement found in payload",
            )

    def store_last_vaccination(self):
        self.last_vc =

    def is_vaccine_ema(self, vaccine_info: dict):
        vaccine_type = vaccine_info["mp"]
        if vaccine_type in VACCINES_EMA_LIST:
            return True
        if vaccine_type == SPUTNIK and vaccine_info["co"] == "SM":
            return True

        return False
