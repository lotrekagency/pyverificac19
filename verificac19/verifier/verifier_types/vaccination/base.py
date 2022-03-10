from typing import Union
from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError
from verificac19.exceptions import VerificationComplete as vc
from verificac19.verifier.verifier_types.base import BaseVerifier
from verificac19.verifier.common.result import Result, NOTHING_FOUND_RESULT

from verificac19.verifier.common.info import (
    VACCINES_EMA_LIST,
    SPUTNIK
)

class BaseVaccination(BaseVerifier):

    def __init__(self, dcc: dcc.DCC, *args, **kwargs):
        super().__init__(dcc, *args, **kwargs)
        self.store_last_vaccination()

    def start_verification(self) -> Union[Result, None]:
        self.verify_payload_content()

    def verify_payload_content(self):
        if not self.payload.get("v"):
            raise vc(NOTHING_FOUND_RESULT)
        if len(self.payload["v"]) == 0:
            raise vc(NOTHING_FOUND_RESULT)

    def store_last_vaccination(self) -> None:
        all_vaccinations = self.payload["v"]
        self.last_vc = all_vaccinations[-1]

    def is_vaccine_EMA(self) -> bool:
        vaccine_type = self.last_vc["mp"]
        country = self.last_vc["co"]

        if vaccine_type in VACCINES_EMA_LIST:
            return True
        if vaccine_type == SPUTNIK and country == "SM":
            return True

        return False
