from enum import Enum
from typing import Callable
from datetime import datetime, timedelta
from OpenSSL import crypto

from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError

from verificac19.service import _service as service

from verificac19.verifier.result import Result

from .types import VaccinationVerifier, Verifier
from .common import Codes, Mode

verifier = Verifier()

class Interface:

    def _verify_rules(self, dcc_obj: dcc.DCC, mode: Mode):
        payload = dcc_obj.payload
        if "v" in payload:
            vac_verifier = VaccinationVerifier()
            result = vac_verifier.check_dcc(dcc_obj, mode)
        elif "t" in payload:
            result = verifier._check_test(dcc_obj, mode)
        elif "r" in payload:
            result = verifier._check_recovery(dcc_obj, mode)
        elif "e" in payload:
            result = verifier._check_exemption(dcc_obj, mode)
        else:
            result = Result(
                Codes.NOT_EU_DCC.value,
                False,
                "No vaccination, test or recovery statement found in payload",

   )
        if result._result and not any(
            verifier._verify_uvci(payload, t) for t in ["v", "t", "r", "e"]
        ):
            result = Result(
                Codes.NOT_VALID,
                False,
                "UVCI in blacklist",
            )
        return result.add_person(
            f"{payload['nam']['fn']} {payload['nam']['gn']}", payload["dob"]
        ).payload

    def _verify(
        self,
        f: Callable[[str, DCCParsingError], dcc.DCC],
        path_or_raw: str,
        mode: Mode = None,
    ):
        if mode is None:
            mode = Mode.NORMAL_DGP
        try:
            dcc = f(path_or_raw)
            if not verifier._verify_dsc(dcc):
                result = Result(
                    verifier.Codes.NOT_VALID.value,
                    False,
                    "Signature is not valid",
                )
                if "nam" in dcc.payload:
                    result = result.add_person(
                        f"{dcc.payload['nam']['fn']} {dcc.payload['nam']['gn']}",
                        dcc.payload["dob"],
                    )
                return result.payload
            response = self._verify_rules(dcc, mode)
            return response
        except DCCParsingError:
            return Result(
                Codes.NOT_EU_DCC.value,
                False,
                "Certificate is not valid",
            ).payload

    def verify_image(self, path: str, mode: Mode = None):
        return self._verify(dcc.from_image, path, mode)

    def verify_raw(self, raw: str, mode: Mode = None):
        return self._verify(dcc.from_raw, raw, mode)


