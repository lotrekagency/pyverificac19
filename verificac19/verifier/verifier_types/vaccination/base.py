from typing import Union
from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError
from ..base import BaseVerifier
from verificac19.verifier.common.result import Result, NOTHING_FOUND_RESULT, ResultOrNone
from verificac19.verifier.decorators import VerifierCheck

from verificac19.verifier.common.info import (
    VACCINES_EMA_LIST,
    SPUTNIK
)

class BaseVaccination(BaseVerifier):

    def __init__(self, dcc: dcc.DCC, *args, **kwargs):
        super().__init__(dcc, *args, **kwargs)
        self.store_last_vaccination()

    @VerifierCheck()
    def verify_payload_content(self) -> ResultOrNone:
        if not self.payload.get("v"):
            return NOTHING_FOUND_RESULT
        if len(self.payload["v"]) == 0:
            return NOTHING_FOUND_RESULT

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
